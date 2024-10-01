# Usage

```python
import starlette.applications
import starlette_problem.handler


app = starlette.applications.Starlette()
starlette_problem.handler.add_exception_handler(app)
```

A custom logger can be provided using:

```python
add_exception_handler(
    app,
    logger=...,
)
```

If you require cors headers, you can pass a `starlette_problem.cors.CorsConfiguration`
instance to `add_exception_handler(cors=...)`.

```python
add_exception_handler(
    app,
    cors=CorsConfiguration(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
)
```

To customise the way that errors, that are not a subclass of Problem, are
handled provide `unhandled_wrappers`, a dict mapping an http status code to
a `StatusProblem`, the system key `default` is also accepted as the root wrapper
for all unhandled exceptions.

```python
from starlette_problem.error import StatusProblem
from starlette_problem.handler import add_exception_handler

class NotFoundError(StatusProblem):
    status = 404
    message = "Endpoint not found."

add_exception_handler(
    app,
    unhandled_wrappers={
        "404": NotFoundError,
    },
)
```

If you wish to hide debug messaging from external users, `StripExtrasPostHook`
allows modifying the response content. `mandatory_fields` supports defining
fields that should always be returned, default fields are `["type", "title",
"status", "detail"]`.

For more fine-grained control, `exclude_status_codes=[500, ...]` can be used to
allow extras for specific status codes. Alternatively if you have a lot of
exclusions, `include_status_codes=[400, ...]` can be used to determine which
status_codes to strip extras for. Allowing expected fields to reach the user,
while suppressing unexpected server errors etc.

```python
from starlette_problem.handler import StripExtrasPostHook, add_exception_handler

add_exception_handler(
    app,
    post_hooks=[
        StripExtrasPostHook(
            mandatory_fields=["type", "title", "status", "detail", "custom-extra"],
            exclude_status_codes=[400],
            enabled=True,
        )
    ],
)
```

## Sentry

`starlette_problem` is designed to play nicely with [Sentry](https://sentry.io),
there is no need to do anything special to integrate with sentry other than
initializing the sdk. The Starlette integration paired with the
Logging integration will take care of everything.

To prevent duplicated entries, ignoing the `uvicorn.error` logger in sentry can
be handy.
