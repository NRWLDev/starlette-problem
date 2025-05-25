"""
Run this example:
$ uvicorn examples.openapi:app

To see an openapi schema response
$ curl http://localhost:8000/schema

To see an openapi.json response
$ curl http://localhost:8000/openapi.json
"""

import logging

import starlette.applications
from starlette.routing import Route

from starlette_problem.schemas import SchemaGenerator
from starlette_problem.error import NotFoundProblem


class UserNotFoundError(NotFoundProblem):
    title = "User not found"


schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}},
    problems=[UserNotFoundError],
)

logging.getLogger("uvicorn.error").disabled = True


def list_users():
    """
    responses:
      200:
        description: A list of users.
        examples:
          [{"username": "tom"}, {"username": "lucy"}]
    """
    return []


def get_user():
    """
    responses:
      200:
        description: Get a specific user.
        examples:
          {"username": "tom"}
      404:
        content:
          application/problem+json:
            schema:
              $ref: '#/components/schemas/UserNotFoundError'
    """
    raise UserNotFoundError("Can not find user.")


def openapi_schema(request):
    return schemas.OpenAPIResponse(request=request)


def openapi_json(request):
    return schemas.OpenAPIJsonResponse(request=request)


app = starlette.applications.Starlette(
    routes=[
        Route("/user", list_users, methods=["GET"]),
        Route("/user/{id}", get_user, methods=["GET"]),
        Route("/schema", endpoint=openapi_schema, include_in_schema=False),
        Route("/openapi.json", endpoint=openapi_json, include_in_schema=False),
    ],
)


if __name__ == "__main__":
    app.run()
