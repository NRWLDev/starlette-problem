import httpx
import pytest
from starlette.applications import Starlette
from starlette.routing import Route

from starlette_problem.error import UnauthorisedProblem
from starlette_problem.schemas import SchemaGenerator


@pytest.fixture
def app():
    schemas = SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}},
        generic_defaults=True,
        problems=[UnauthorisedProblem],
    )

    def list_users(request):
        """
        responses:
          200:
            description: A list of users.
            examples:
              [{"username": "tom"}, {"username": "lucy"}]
        """
        raise NotImplementedError

    def create_user(request):
        """
        responses:
          200:
            description: A user.
            examples:
              {"username": "tom"}
        """
        raise NotImplementedError

    def openapi_schema(request):
        return schemas.OpenAPIResponse(request=request)

    def openapi_json(request):
        return schemas.OpenAPIJsonResponse(request=request)

    routes = [
        Route("/users", endpoint=list_users, methods=["GET"]),
        Route("/users", endpoint=create_user, methods=["POST"]),
        Route("/schema", endpoint=openapi_schema, include_in_schema=False),
        Route("/openapi.json", endpoint=openapi_json, include_in_schema=False),
    ]

    return Starlette(routes=routes)


async def test_openapi_schema(app):
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/schema")
    assert (
        r.content
        == b"""components:
  schemas:
    Problem:
      properties:
        detail:
          anyOf:
          - type: string
          - type: 'null'
          title: Problem detail
        status:
          title: Status code
          type: integer
        title:
          title: Problem title
          type: string
        type:
          title: Problem type
          type: string
      required:
      - type
      - title
      - status
      title: Problem
      type: object
    UnauthorisedProblem:
      properties:
        detail:
          anyOf:
          - type: string
          - type: 'null'
          title: Problem detail
        status:
          title: Status code
          type: integer
        title:
          title: Problem title
          type: string
        type:
          title: Problem type
          type: string
      required:
      - type
      - title
      - status
      title: UnauthorisedProblem
      type: object
info:
  title: Example API
  version: '1.0'
openapi: 3.0.0
paths:
  /users:
    get:
      responses:
        200:
          description: A list of users.
          examples:
          - username: tom
          - username: lucy
        4XX:
          content:
            application/problem+json:
              example:
                detail: Additional error context.
                status: 400
                title: User facing error message.
                type: client-error-type
              schema:
                $ref: '#/components/schemas/Problem'
          description: Client Error
        5XX:
          content:
            application/problem+json:
              example:
                detail: Additional error context.
                status: 500
                title: User facing error message.
                type: server-error-type
              schema:
                $ref: '#/components/schemas/Problem'
          description: Server Error
    post:
      responses:
        200:
          description: A user.
          examples:
            username: tom
        4XX:
          content:
            application/problem+json:
              example:
                detail: Additional error context.
                status: 400
                title: User facing error message.
                type: client-error-type
              schema:
                $ref: '#/components/schemas/Problem'
          description: Client Error
        5XX:
          content:
            application/problem+json:
              example:
                detail: Additional error context.
                status: 500
                title: User facing error message.
                type: server-error-type
              schema:
                $ref: '#/components/schemas/Problem'
          description: Server Error
"""
    )


async def test_openapi_json(app):
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/openapi.json")
    assert r.json() == {
        "components": {
            "schemas": {
                "Problem": {
                    "properties": {
                        "detail": {
                            "anyOf": [
                                {
                                    "type": "string",
                                },
                                {
                                    "type": "null",
                                },
                            ],
                            "title": "Problem detail",
                        },
                        "status": {
                            "title": "Status code",
                            "type": "integer",
                        },
                        "title": {
                            "title": "Problem title",
                            "type": "string",
                        },
                        "type": {
                            "title": "Problem type",
                            "type": "string",
                        },
                    },
                    "required": [
                        "type",
                        "title",
                        "status",
                    ],
                    "title": "Problem",
                    "type": "object",
                },
                "UnauthorisedProblem": {
                    "properties": {
                        "detail": {
                            "anyOf": [
                                {
                                    "type": "string",
                                },
                                {
                                    "type": "null",
                                },
                            ],
                            "title": "Problem detail",
                        },
                        "status": {
                            "title": "Status code",
                            "type": "integer",
                        },
                        "title": {
                            "title": "Problem title",
                            "type": "string",
                        },
                        "type": {
                            "title": "Problem type",
                            "type": "string",
                        },
                    },
                    "required": [
                        "type",
                        "title",
                        "status",
                    ],
                    "title": "UnauthorisedProblem",
                    "type": "object",
                },
            },
        },
        "info": {
            "title": "Example API",
            "version": "1.0",
        },
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "A list of users.",
                            "examples": [
                                {
                                    "username": "tom",
                                },
                                {
                                    "username": "lucy",
                                },
                            ],
                        },
                        "4XX": {
                            "content": {
                                "application/problem+json": {
                                    "example": {
                                        "detail": "Additional error context.",
                                        "status": 400,
                                        "title": "User facing error message.",
                                        "type": "client-error-type",
                                    },
                                    "schema": {
                                        "$ref": "#/components/schemas/Problem",
                                    },
                                },
                            },
                            "description": "Client Error",
                        },
                        "5XX": {
                            "content": {
                                "application/problem+json": {
                                    "example": {
                                        "detail": "Additional error context.",
                                        "status": 500,
                                        "title": "User facing error message.",
                                        "type": "server-error-type",
                                    },
                                    "schema": {
                                        "$ref": "#/components/schemas/Problem",
                                    },
                                },
                            },
                            "description": "Server Error",
                        },
                    },
                },
                "post": {
                    "responses": {
                        "200": {
                            "description": "A user.",
                            "examples": {
                                "username": "tom",
                            },
                        },
                        "4XX": {
                            "content": {
                                "application/problem+json": {
                                    "example": {
                                        "detail": "Additional error context.",
                                        "status": 400,
                                        "title": "User facing error message.",
                                        "type": "client-error-type",
                                    },
                                    "schema": {
                                        "$ref": "#/components/schemas/Problem",
                                    },
                                },
                            },
                            "description": "Client Error",
                        },
                        "5XX": {
                            "content": {
                                "application/problem+json": {
                                    "example": {
                                        "detail": "Additional error context.",
                                        "status": 500,
                                        "title": "User facing error message.",
                                        "type": "server-error-type",
                                    },
                                    "schema": {
                                        "$ref": "#/components/schemas/Problem",
                                    },
                                },
                            },
                            "description": "Server Error",
                        },
                    },
                },
            },
        },
    }


async def test_additional_keys_in_base_schema():
    schemas = SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}, "components": {"schemas": {}}},
        generic_defaults=True,
        problems=[UnauthorisedProblem],
    )

    def openapi_json(request):
        return schemas.OpenAPIJsonResponse(request=request)

    routes = [
        Route("/openapi.json", endpoint=openapi_json, include_in_schema=False),
    ]

    app = Starlette(routes=routes)

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/openapi.json")
    data = r.json()
    assert "Problem" in data["components"]["schemas"]


async def test_no_generic_defaults():
    schemas = SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}, "components": {"schemas": {}}},
        generic_defaults=False,
    )

    def list_users(request):
        """
        responses:
          200:
            description: A list of users.
            examples:
              [{"username": "tom"}, {"username": "lucy"}]
        """
        raise NotImplementedError

    def openapi_json(request):
        return schemas.OpenAPIJsonResponse(request=request)

    routes = [
        Route("/users", endpoint=list_users, methods=["GET"]),
        Route("/openapi.json", endpoint=openapi_json, include_in_schema=False),
    ]

    app = Starlette(routes=routes)

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False, client=("1.2.3.4", 123))
    client = httpx.AsyncClient(transport=transport, base_url="https://test")

    r = await client.get("/openapi.json")
    data = r.json()
    assert "4XX" not in data["paths"]["/users"]["get"]["responses"]
