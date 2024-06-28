"""
Run this example:
$ uvicorn examples.basic:app

To see a standard expected user error response.
$ curl http://localhost:8000/user-error

To see a standard expected server error response.
$ curl http://localhost:8000/user-error
"""

import logging

import starlette.applications
from starlette.routing import Route

from starlette_problem.error import BadRequestProblem, ServerProblem
from starlette_problem.handler import add_exception_handler

logging.getLogger("uvicorn.error").disabled = True


class KnownProblem(BadRequestProblem):
    title = "Something we know about happened."


class KnownServerProblem(ServerProblem):
    title = "Something you can't do anything about happened."


async def user_error(request) -> dict:
    raise KnownProblem("A known user error use case occurred.")


async def server_error(request) -> dict:
    raise KnownServerProblem("A known server error use case occurred.")


app = starlette.applications.Starlette(
    routes=[
        Route("/user-error", user_error, methods=["GET"]),
        Route("/server-error", server_error, methods=["GET"]),
    ],
)

add_exception_handler(
    app,
)


if __name__ == "__main__":
    app.run()
