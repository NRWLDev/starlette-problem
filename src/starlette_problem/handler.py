from __future__ import annotations

import http
import json
import typing as t
from warnings import warn

import rfc9457
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from starlette_problem.error import Problem, StatusProblem
from starlette_problem.util import convert_status_code

if t.TYPE_CHECKING:
    import logging

    from starlette.applications import Starlette

    from starlette_problem.cors import CorsConfiguration


Handler = t.Callable[["ExceptionHandler", Request, Exception], t.Optional[Problem]]
PreHook = t.Callable[[Request, Exception], None]
PostHook = t.Callable[[dict, Request, Response], tuple[dict, Response]]


def http_exception_handler(eh: ExceptionHandler, _request: Request, exc: HTTPException) -> Problem:
    wrapper = eh.unhandled_wrappers.get(str(exc.status_code))
    title, type_ = convert_status_code(exc.status_code)
    detail = exc.detail
    return (
        wrapper(detail, headers=exc.headers)
        if wrapper
        else Problem(
            title=title,
            type_=type_,
            detail=detail,
            status=exc.status_code,
            headers=exc.headers,
        )
    )


class ExceptionHandler:
    def __init__(  # noqa: PLR0913
        self: t.Self,
        logger: logging.Logger | None = None,
        unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
        handlers: dict[type[Exception], Handler] | None = None,
        pre_hooks: list[PreHook] | None = None,
        post_hooks: list[PostHook] | None = None,
        documentation_base_url: str | None = None,
        documentation_uri_template: str = "",
        *,
        strip_debug: bool | None = None,
        strip_debug_codes: list[int] | None = None,
        strict_rfc9457: bool = False,
    ) -> None:
        self.logger = logger
        self.unhandled_wrappers = unhandled_wrappers or {}
        self.handlers = handlers or {}
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []
        self.documentation_uri_template = documentation_uri_template
        if not documentation_uri_template and documentation_base_url:
            self.documentation_uri_template = f"{documentation_base_url.rstrip('/')}/{{type}}"
        self.strip_debug = strip_debug
        self.strip_debug_codes = strip_debug_codes or []
        self.strict = strict_rfc9457

        if strip_debug is not None or strip_debug_codes is not None:
            warn(
                "Using deprecated parameter 'strip_debug' or `strip_debug_codes`, switch to 'StripExtrasPostHook'.",
                FutureWarning,
                stacklevel=2,
            )

        if documentation_base_url:
            warn(
                "Using deprecated parameter 'documentation_base_url', switch to 'documentation_uri_template'",
                FutureWarning,
                stacklevel=2,
            )

    def __call__(self: t.Self, request: Request, exc: Exception) -> Response:  # noqa: C901
        for pre_hook in self.pre_hooks:
            pre_hook(request, exc)

        wrapper = self.unhandled_wrappers.get("default", self.unhandled_wrappers.get("500"))
        ret = (
            wrapper(str(exc))
            if wrapper
            else Problem(
                title="Unhandled exception occurred.",
                detail=str(exc),
                type_="unhandled-exception",
            )
        )

        for exc_type, handler in self.handlers.items():
            if isinstance(exc, exc_type):
                response = handler(self, request, exc)
                if response is not None:
                    ret = response
                    break

        if isinstance(exc, rfc9457.Problem):
            ret = exc

        if ret.status >= http.HTTPStatus.INTERNAL_SERVER_ERROR and self.logger:
            self.logger.exception(ret.title, exc_info=(type(exc), exc, exc.__traceback__))

        strip_debug_ = self.strip_debug or ret.status in self.strip_debug_codes

        if strip_debug_ and (ret.detail or ret.extras) and self.logger:
            msg = "Stripping debug information from exception."
            self.logger.debug(msg)

            for k, v in {
                "detail": ret.detail,
                **ret.extras,
            }.items():
                msg = f"Removed {k}: {v}"
                self.logger.debug(msg)

        headers = {"content-type": "application/problem+json"}
        headers.update(ret.headers or {})

        content = ret.marshal(
            uri=self.documentation_uri_template,
            strip_debug=strip_debug_,
            strict=self.strict,
        )
        response = JSONResponse(
            status_code=ret.status,
            content=content,
            headers=headers,
        )

        for post_hook in self.post_hooks:
            result = post_hook(content, request, response)
            if isinstance(result, Response):
                response = result
                warn(
                    f"PostHook {post_hook.__class__.__name__} returning deprecated format `return response`, use `return (content, response)`.",
                    FutureWarning,
                    stacklevel=2,
                )
            else:
                content, response = result

        return response


class CorsPostHook:
    def __init__(self: t.Self, config: CorsConfiguration) -> None:
        self.config = config

    def __call__(self: t.Self, _content: dict, request: Request, response: Response) -> Response:
        # Since the CORSMiddleware is not executed when an unhandled server exception
        # occurs, we need to manually set the CORS headers ourselves if we want the FE
        # to receive a proper JSON 500, opposed to a CORS error.
        # Setting CORS headers on server errors is a bit of a philosophical topic of
        # discussion in many frameworks.
        # See dotnet core for a recent discussion, where ultimately it was
        # decided to return CORS headers on server failures:
        # https://github.com/dotnet/aspnetcore/issues/2378
        origin = request.headers.get("origin")

        if origin:
            # Have the middleware do the heavy lifting for us to parse
            # all the config, then update our response headers
            mw = CORSMiddleware(
                app=None,
                allow_origins=self.config.allow_origins,
                allow_credentials=self.config.allow_credentials,
                allow_methods=self.config.allow_methods,
                allow_headers=self.config.allow_headers,
            )

            # Logic directly from Starlette"s CORSMiddleware:
            # https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py#L152

            response.headers.update(mw.simple_headers)
            has_cookie = "cookie" in request.headers

            # If request includes any cookie headers, then we must respond
            # with the specific origin instead of "*".
            if mw.allow_all_origins and has_cookie:
                response.headers["Access-Control-Allow-Origin"] = origin

            # If we only allow specific origins, then we have to mirror back
            # the Origin header in the response.
            elif not mw.allow_all_origins and mw.is_allowed_origin(origin=origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers.add_vary_header("Origin")

        return response


class StripExtrasPostHook:
    def __init__(
        self: t.Self,
        logger: logging.Logger | None = None,
        mandatory_fields: list[str] | None = None,
        exclude_status_codes: list[int] | None = None,
        include_status_codes: list[int] | None = None,
        *,
        enabled: bool = False,
    ) -> None:
        self.mandatory_fields = mandatory_fields or ["type", "title", "status", "detail"]
        self.enabled = enabled
        self.exclude_status_codes = exclude_status_codes or []
        self.include_status_codes = include_status_codes or []
        self.logger = logger

    def __call__(self: t.Self, content: dict, _request: Request, response: JSONResponse) -> JSONResponse:
        strip_extras = self.enabled and (
            response.status_code in self.include_status_codes or response.status_code not in self.exclude_status_codes
        )

        new_content = content.copy()
        if strip_extras:
            msg = "Stripping debug information from exception."
            self.logger.debug(msg) if self.logger else None

            for k, v in content.items():
                if k not in self.mandatory_fields:
                    msg = f"Removed {k}: {v}"
                    self.logger.debug(msg) if self.logger else None
                    new_content.pop(k)

            response.body = json.dumps(new_content, separators=(",", ":")).encode("utf-8")

        return new_content, response


def generate_handler(  # noqa: PLR0913
    logger: logging.Logger | None = None,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[type[Exception], Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    documentation_base_url: str | None = None,
    documentation_uri_template: str = "",
    *,
    strip_debug: bool | None = None,
    strip_debug_codes: list[int] | None = None,
    strict_rfc9457: bool = False,
) -> t.Callable:
    handlers = handlers or {}
    handlers.update(
        {
            HTTPException: http_exception_handler,
        },
    )
    pre_hooks = pre_hooks or []
    post_hooks = post_hooks or []

    if cors:
        # Ensure runs before custom modifications
        post_hooks.insert(0, CorsPostHook(cors))

    return ExceptionHandler(
        logger=logger,
        unhandled_wrappers=unhandled_wrappers,
        handlers=handlers,
        pre_hooks=pre_hooks,
        post_hooks=post_hooks,
        documentation_base_url=documentation_base_url,
        documentation_uri_template=documentation_uri_template,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
        strict_rfc9457=strict_rfc9457,
    )


def add_exception_handler(  # noqa: PLR0913
    app: Starlette,
    logger: logging.Logger | None = None,
    cors: CorsConfiguration | None = None,
    unhandled_wrappers: dict[str, type[StatusProblem]] | None = None,
    handlers: dict[type[Exception], Handler] | None = None,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    documentation_base_url: str | None = None,
    documentation_uri_template: str = "",
    *,
    strip_debug: bool | None = False,
    strip_debug_codes: list[int] | None = None,
    strict_rfc9457: bool = False,
) -> None:
    eh = generate_handler(
        logger,
        cors,
        unhandled_wrappers,
        handlers,
        pre_hooks,
        post_hooks,
        documentation_base_url,
        documentation_uri_template,
        strip_debug=strip_debug,
        strip_debug_codes=strip_debug_codes,
        strict_rfc9457=strict_rfc9457,
    )

    app.add_exception_handler(Exception, eh)
    app.add_exception_handler(rfc9457.Problem, eh)
    app.add_exception_handler(HTTPException, eh)
