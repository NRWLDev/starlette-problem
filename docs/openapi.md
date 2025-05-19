# Openapi Support

`starlette-problem` expands on the builtin support for openapi generation
described [here](https://www.starlette.io/schemas/) to provide Problem
component and response generation.

On top of the base schema generation, some additional init parameters have been
introduced to configure problem component definition in line with the exception
handler configuration.

## Custom components
As a default, the schema generator will inject a `Problem` component that can
be used in docstrings when defining an error response. If there is one or more
specific Problem subclasses that are convenient to include in the openapi
component definition, these can be passed in with the schema definition.

```python
from starlette_problem.schemas import SchemaGenerator

schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}},
    problems=[UnauthorisedProblem],
)
```

## Response customisation
General usage is to define a response object linked to a component in the docstring.

```python
def list_users(request):
    """
    responses:
      200:
        description: A list of users.
        examples:
          [{"username": "tom"}, {"username": "lucy"}]
      401:
        content:
          application/problem+json:
            schema:
              $ref: '#/components/schemas/UnauthorisedProblem'
    """
```

A generic `4XX` and `5XX` response can be added to each path, these can be
opted into by passing `generic_defaults=True` when defining the schema object.


```python
from starlette_problem.schemas import SchemaGenerator

schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}},
    generic_defaults=True,
)
```

If the `starlette-problem` exception handler has been defined with a custom
documentation uri, or in strict mode, these can both be defined with the schema
definition to ensure documentation lines up with reality.

```python
from starlette_problem.schemas import SchemaGenerator

schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}},
    documentation_uri_template="my_uri_template",
    strict=True,
)
```

## openapi.json
In addition to the supported openapi schema response, `starlette-problem`
supports generation of `openapi.json` as well.

```python
def openapi_schema(request):
    return schemas.OpenAPIResponse(request=request)

def openapi_json(request):
    return schemas.OpenAPIJsonResponse(request=request)

routes = [
    Route("/schema", endpoint=openapi_schema, include_in_schema=False),
    Route("/openapi.json", endpoint=openapi_json, include_in_schema=False),
]

app =  Starlette(routes=routes)
```
