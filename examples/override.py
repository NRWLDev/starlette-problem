"""
Run this example:
$ uvicorn examples.override:app

To see a custom starlette 405 error response.
$ curl http://localhost:8000/not-allowed

To see a custom starlette 404 error response.
$ curl http://localhost:8000/not-found
"""

import logging

import starlette.requests
import starlette.applications
from starlette.exceptions import HTTPException
from starlette.routing import Route

from starlette_problem.handler import ExceptionHandler, add_exception_handler
from starlette_problem.error import NotFoundProblem, Problem, StatusProblem

logging.getLogger("uvicorn.error").disabled = True


class CustomNotFoundProblem(NotFoundProblem):
    title = "Endpoint not available."


class CustomNotAllowedProblem(StatusProblem):
    status = 405
    title = "Method not allowed."


status_mapping = {
    "404": (CustomNotFoundProblem, "The requested endpoint does not exist."),
    "405": (CustomNotAllowedProblem, "This method is not allowed."),
}


def http_exception_handler(
    _eh: ExceptionHandler,
    _request: starlette.requests.Request,
    exc: HTTPException,
) -> Problem:
    exc_, detail = status_mapping.get(str(exc.status_code))
    return exc_(detail)


async def method_not_allowed() -> dict:
    return {}


app = starlette.applications.Starlette(
    routes=[
        Route("/not-allowed", method_not_allowed, methods=["POST"]),
    ],
)

add_exception_handler(
    app,
    http_exception_handler=http_exception_handler,
)


if __name__ == "__main__":
    app.run()
