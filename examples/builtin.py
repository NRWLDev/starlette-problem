"""
Run this example:
$ uvicorn examples.builtin:app

To see a standard unhandled server error response.
$ curl http://localhost:8000/unexpected-error

To see a standard starlette 405 error response.
$ curl http://localhost:8000/not-allowed

To see a standard starlette 404 error response.
$ curl http://localhost:8000/not-found
"""

import logging

import starlette.applications
from starlette.routing import Route

from starlette_problem.handler import add_exception_handler

logging.getLogger("uvicorn.error").disabled = True


async def method_not_allowed(request) -> dict:
    return {}


async def unexpected_error(request) -> dict:
    return {"value": 1 / 0}


app = starlette.applications.Starlette(
    routes=[
        Route("/not-allowed", method_not_allowed, methods=["POST"]),
        Route("/unexpected-error", unexpected_error, methods=["GET"]),
    ],
)

add_exception_handler(
    app,
)


if __name__ == "__main__":
    app.run()
