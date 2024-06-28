"""
Run this example:
$ uvicorn examples.auth:app

To see a 401 response.
$ curl http://localhost:8000/authorized

To see a 403 response.
$ curl http://localhost:8000/authorized -H "Authorization: Bearer not-permitted"

To see an authorized response.
$ curl http://localhost:8000/authorized -H "Authorization: Bearer permitted"
"""

import starlette
import starlette.applications
from starlette.routing import Route
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from starlette_problem.error import (
    ForbiddenProblem,
    UnauthorisedProblem,
)
from starlette_problem.handler import add_exception_handler


class AuthorizationRequiredError(UnauthorisedProblem):
    title = "Authorization token required."


class PermissionRequiredError(ForbiddenProblem):
    title = "Permission required."


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            msg = "Missing Authorization header."
            raise AuthorizationRequiredError(msg)

        auth = conn.headers["Authorization"]
        scheme, credentials = auth.split()
        if credentials != "permitted":
            msg = "No active permissions."
            raise PermissionRequiredError(msg)

        return AuthCredentials(["authenticated"]), SimpleUser("username")


async def authorized(request) -> dict:
    return JSONResponse(content={"authorized": request.user.is_authenticated})


app = starlette.applications.Starlette(
    routes=[
        Route("/authorized", authorized, methods=["GET"]),
    ],
    middleware=[Middleware(AuthenticationMiddleware, backend=BasicAuthBackend())],
)

add_exception_handler(
    app,
)
