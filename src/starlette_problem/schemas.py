from __future__ import annotations

import json
import typing as t

from rfc9457 import Problem
from rfc9457.openapi import problem_component, problem_response
from starlette.responses import Response
from starlette.schemas import SchemaGenerator as SchemaGenerator_

if t.TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.routing import BaseRoute


class OpenAPIJsonResponse(Response):
    media_type = "application/vnd.github.v3+json"

    def render(self, content: dict) -> bytes:
        return json.dumps(content).encode("utf-8")


class SchemaGenerator(SchemaGenerator_):
    def __init__(
        self,
        base_schema: dict[str, t.Any],
        *,
        problems: list[type[Problem]] | None = None,
        documentation_uri_template: str = "",
        strict: bool = False,
        generic_defaults: bool = False,
    ) -> None:
        super().__init__(base_schema)
        self.problems = problems or []
        self.documentation_uri_template = documentation_uri_template
        self.strict = strict
        self.generic_defaults = generic_defaults

    def get_schema(self, routes: list[BaseRoute]) -> dict[str, t.Any]:
        schema = super().get_schema(routes)
        if "components" not in schema:
            schema["components"] = {}

        if "schemas" not in schema["components"]:
            schema["components"]["schemas"] = {}

        schema["components"]["schemas"]["Problem"] = problem_component("Problem")
        for problem in self.problems:
            schema["components"]["schemas"][problem.__name__] = problem_component(problem.__name__)

        for methods in schema["paths"].values():
            for details in methods.values():
                if self.generic_defaults:
                    user_error = Problem(
                        "User facing error message.",
                        type_="client-error-type",
                        status=400,
                        detail="Additional error context.",
                    )
                    server_error = Problem(
                        "User facing error message.",
                        type_="server-error-type",
                        status=500,
                        detail="Additional error context.",
                    )
                    details["responses"]["4XX"] = problem_response(
                        description="Client Error",
                        examples=[user_error.marshal(uri=self.documentation_uri_template, strict=self.strict)],
                    )
                    details["responses"]["5XX"] = problem_response(
                        description="Server Error",
                        examples=[server_error.marshal(uri=self.documentation_uri_template, strict=self.strict)],
                    )

        return schema

    def OpenAPIJsonResponse(self, request: Request) -> Response:  # noqa: N802
        routes = request.app.routes
        schema = self.get_schema(routes=routes)
        return OpenAPIJsonResponse(schema)
