"""
Run this example:
$ uvicorn examples.custom:app

To see a custom unhandled server error response.
$ curl http://localhost:8000/unexpected-error

To see a custom starlette 405 error response.
$ curl http://localhost:8000/not-allowed

To see a custom starlette 404 error response.
$ curl http://localhost:8000/not-found
"""

import logging

import starlette.applications
from starlette.routing import Route

from starlette_problem.handler import add_exception_handler
from starlette_problem.error import NotFoundProblem, ServerProblem, StatusProblem, UnprocessableProblem

logging.getLogger("uvicorn.error").disabled = True


class CustomNotFound(NotFoundProblem):
    title = "Endpoint not available."


class CustomNotAllowed(StatusProblem):
    title = "Method not available."
    status = 405


class CustomServer(ServerProblem):
    title = "Server failed."


async def method_not_allowed() -> dict:
    return {}


async def unexpected_error() -> dict:
    return {"value": 1 / 0}


app = starlette.applications.Starlette(
    routes=[
        Route("/not-allowed", method_not_allowed, methods=["POST"]),
        Route("/unexpected-error", unexpected_error, methods=["GET"]),
    ],
)

add_exception_handler(
    app,
    unhandled_wrappers={
        "404": CustomNotFound,
        "405": CustomNotAllowed,
        "default": CustomServer,
    },
)


if __name__ == "__main__":
    app.run()
