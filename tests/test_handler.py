import http
import json
from unittest import mock

import httpx
import pytest
from starlette.applications import Starlette
from starlette.exceptions import HTTPException

from starlette_problem import error, handler
from starlette_problem.cors import CorsConfiguration


class SomethingWrongError(error.ServerProblem):
    title = "This is an error."


class CustomUnhandledException(error.ServerProblem):
    title = "Unhandled exception occurred."


class CustomValidationError(error.StatusProblem):
    status = 422
    title = "Request validation error."


@pytest.fixture
def cors():
    return CorsConfiguration(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


class TestExceptionHandler:
    @pytest.mark.parametrize("default_key", ["default", "500"])
    def test_unexpected_error_replaces_code(self, default_key):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(
            logger=logger,
            unhandled_wrappers={
                default_key: CustomUnhandledException,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "detail": "Something went bad",
            "type": "custom-unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_documentation_uri_template(self):
        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
            documentation_uri_template="https://docs/errors/{type}",
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "type": "https://docs/errors/custom-unhandled-exception",
            "status": 500,
            "detail": "Something went bad",
        }

    def test_strict(self):
        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(
            unhandled_wrappers={
                "default": CustomUnhandledException,
            },
            documentation_uri_template="https://docs/errors/{type}",
            strict_rfc9457=True,
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "type": "about:blank",
            "status": 500,
            "detail": "Something went bad",
        }

    def test_strip_extras_post_hook_disabled(self):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad", a="b")

        eh = handler.ExceptionHandler(
            post_hooks=[handler.StripExtrasPostHook()],
        )
        response = eh(request, exc)

        assert (
            response.body
            == b'{"type":"something-wrong","title":"This is an error.","status":500,"a":"b","detail":"something bad"}'
        )
        assert response.headers["content-length"] == "100"

    def test_strip_extras_post_hook_enabled(self):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad", a="b")

        eh = handler.ExceptionHandler(
            post_hooks=[handler.StripExtrasPostHook(enabled=True)],
        )
        response = eh(request, exc)

        assert (
            response.body
            == b'{"type":"something-wrong","title":"This is an error.","status":500,"detail":"something bad"}'
        )
        assert response.headers["content-length"] == "92"

    def test_strip_extras_post_hook_exclude_status_code(self):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad", a="b")

        eh = handler.ExceptionHandler(
            post_hooks=[handler.StripExtrasPostHook(exclude_status_codes=[500], enabled=True)],
        )
        response = eh(request, exc)

        assert (
            response.body
            == b'{"type":"something-wrong","title":"This is an error.","status":500,"a":"b","detail":"something bad"}'
        )

    def test_strip_extras_post_hook_include_status_code(self):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad", a="b")

        eh = handler.ExceptionHandler(
            post_hooks=[handler.StripExtrasPostHook(include_status_codes=[500], enabled=True)],
        )
        response = eh(request, exc)

        assert (
            response.body
            == b'{"type":"something-wrong","title":"This is an error.","status":500,"detail":"something bad"}'
        )

    def test_strip_extras_post_hook_include_status_code_correctly_allows_other_codes_through(self):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad", a="b")

        eh = handler.ExceptionHandler(
            post_hooks=[handler.StripExtrasPostHook(include_status_codes=[400], enabled=True)],
        )
        response = eh(request, exc)

        assert (
            response.body
            == b'{"type":"something-wrong","title":"This is an error.","status":500,"a":"b","detail":"something bad"}'
        )

    def test_strip_extras_post_hook_custom_mandatory(self):
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad", a="b")

        eh = handler.ExceptionHandler(
            post_hooks=[handler.StripExtrasPostHook(mandatory_fields=["type", "title", "status", "a"], enabled=True)],
        )
        response = eh(request, exc)

        assert response.body == b'{"type":"something-wrong","title":"This is an error.","status":500,"a":"b"}'

    def test_unexpected_error(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(logger=logger)
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "detail": "Something went bad",
            "type": "unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_error_handler_can_pass(self):
        def pass_handler(_eh, _request, _exc):
            return None

        def handler_(_eh, _request, exc):
            return error.Problem(
                title="Handled",
                type_="handled-error",
                detail=str(exc),
                status=500,
                headers=None,
            )

        request = mock.Mock()
        exc = RuntimeError("Something went bad")

        eh = handler.ExceptionHandler(handlers={RuntimeError: pass_handler, Exception: handler_})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "Handled",
            "detail": "Something went bad",
            "type": "handled-error",
            "status": 500,
        }

    def test_error_handler_breaks_at_first_bite(self):
        def handler_(_eh, _request, exc):
            return error.Problem(
                title="Handled",
                type_="handled-error",
                detail=str(exc),
                status=400,
                headers=None,
            )

        def unused_handler(_eh, _request, _exc):
            return error.Problem(
                title="Handled",
                type_="handled-error",
                detail=str(exc),
                status=500,
                headers=None,
            )

        request = mock.Mock()
        exc = RuntimeError("Something went bad")

        eh = handler.ExceptionHandler(handlers={RuntimeError: handler_, Exception: unused_handler})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert json.loads(response.body) == {
            "title": "Handled",
            "detail": "Something went bad",
            "type": "handled-error",
            "status": 400,
        }

    def test_error_handler_pass(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = Exception("Something went bad")

        eh = handler.ExceptionHandler(logger=logger)
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.headers["content-type"] == "application/problem+json"
        assert json.loads(response.body) == {
            "title": "Unhandled exception occurred.",
            "detail": "Something went bad",
            "type": "unhandled-exception",
            "status": 500,
        }
        assert logger.exception.call_args == mock.call(
            "Unhandled exception occurred.",
            exc_info=(type(exc), exc, None),
        )

    def test_starlette_error(self):
        request = mock.Mock()
        exc = HTTPException(404)

        eh = handler.ExceptionHandler(handlers={HTTPException: handler.http_exception_handler_})
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.NOT_FOUND
        assert json.loads(response.body) == {
            "title": "Not Found",
            "detail": "Not Found",
            "type": "http-not-found",
            "status": 404,
        }

    def test_starlette_error_custom_wrapper(self):
        request = mock.Mock()
        exc = HTTPException(404)

        eh = handler.ExceptionHandler(
            handlers={HTTPException: handler.http_exception_handler_},
            unhandled_wrappers={
                "404": SomethingWrongError,
            },
        )
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "This is an error.",
            "detail": "Not Found",
            "type": "something-wrong",
            "status": 500,
        }

    def test_known_error(self):
        request = mock.Mock()
        exc = SomethingWrongError("something bad")

        eh = handler.ExceptionHandler()
        response = eh(request, exc)

        assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(response.body) == {
            "title": "This is an error.",
            "detail": "something bad",
            "type": "something-wrong",
            "status": 500,
        }

    def test_error_with_no_origin(self, cors):
        app = Starlette()
        request = mock.Mock(headers={})
        exc = SomethingWrongError("something bad")

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers

    def test_error_with_origin(self, cors):
        app = Starlette()
        request = mock.Mock(headers={"origin": "localhost"})
        exc = SomethingWrongError("something bad")

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"

    def test_error_with_origin_and_cookie(self, cors):
        app = Starlette()
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins(self, cors):
        app = Starlette()
        request = mock.Mock(headers={"origin": "localhost", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" in response.headers
        assert response.headers["vary"] == "Origin"
        assert response.headers["access-control-allow-origin"] == "localhost"

    def test_missing_token_with_origin_limited_origins_no_match(self, cors):
        app = Starlette()
        request = mock.Mock(headers={"origin": "localhost2", "cookie": "something"})
        exc = SomethingWrongError("something bad")

        cors.allow_origins = ["localhost"]

        eh = handler.add_exception_handler(
            app=app,
            cors=cors,
        )
        response = eh(request, exc)

        assert "access-control-allow-origin" not in response.headers

    def test_pre_hook(self):
        logger = mock.Mock()

        request = mock.Mock()
        exc = ValueError("Something went bad")

        def hook(_request, exc) -> None:
            logger.debug(str(type(exc)))

        eh = handler.ExceptionHandler(
            logger=logger,
            pre_hooks=[hook],
        )
        eh(request, exc)

        assert logger.debug.call_args == mock.call("<class 'ValueError'>")


async def test_exception_handler_in_app():
    m = mock.Mock()

    def pre_hook(_req, _exc):
        m.call("pre-hook")

    app = Starlette()

    handler.add_exception_handler(
        app=app,
        pre_hooks=[pre_hook],
        unhandled_wrappers={
            "422": CustomValidationError,
            "default": CustomUnhandledException,
        },
    )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "http-not-found",
        "title": "Not Found",
        "detail": "Not Found",
        "status": 404,
    }
    assert m.call.call_args == mock.call("pre-hook")


async def test_exception_handler_in_app_post_register():
    app = Starlette()

    handler.add_exception_handler(
        app=app,
        unhandled_wrappers={
            "422": CustomValidationError,
            "default": CustomUnhandledException,
        },
    )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "http-not-found",
        "title": "Not Found",
        "detail": "Not Found",
        "status": 404,
    }


async def test_custom_http_exception_handler_in_app():
    def custom_handler(_eh, _request, _exc) -> error.Problem:
        return error.Problem("a problem")

    app = Starlette()

    handler.add_exception_handler(
        app=app,
        http_exception_handler=custom_handler,
    )

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/endpoint")
    assert r.json() == {
        "type": "problem",
        "title": "a problem",
        "status": 500,
    }
