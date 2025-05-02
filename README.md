## IMAGO Coding Challenge

### How to run the application?

I recommend you to clone the repository locally and run the docker referring the following command.
Set the environment variables for ElasticSearch and install the system.


```shell
cp .env.example .env
docker compose up –build
```

Testing can be done inside the running container (unittest, backend only)

```shell
docker exec -it app-backend-1 poetry run pytest /backend/tests
```
---

- **Tools and Frameworks Disclaimer**: ReactJS is chosen for the frontend and FastAPI (Python) for the backend. Poetry helps with dependency management, while Docker and CodeSandbox simplify deployment. Testing is integrated into the development lifecycle via Pytest. Note that the chosen tools and frameworks are based on personal preference and do not imply that they are superior to alternatives.

- **ElasticSearch** (Search Indexes) as Data Store: At the beginning of the task, I was a bit confused, because so far I have thought of ElasticSearch to be rather not holding an authoritative version(a.k.a., source of truth) of data. For a moment, I was thinking of (somehow) normalizing the data if I am supposed to build a system. And then I got reminded that redundancy(or denormalization) is pretty often essential for getting good performance on read queries.

- **Schema**: Search queries are formed referring to the field mapping, which can be fetched via `GET /imago/_mapping`. One noticeable point is that the dynamic mapping is enabled. Which might lead to eventual data inconsistency.

- I can see many missing fields, for example, `bearbeitet_bild` and `description` nearly have no value. And if this is inconsistent among documents, this unexpectedness should be handled all in the frontend, backend, data store, analytics layers which could be sometimes pretty tricky. And if this is too costly to ignore, we might need to consider schema enforcement (but still need to think about what to do to heal the current situation).

- In a similar context, we can introduce, for example, Pydantic to the current setup, if needed.

- **Pagination**: When the search response exceeds 20 items (or other given number, can be set to pageSize at frontend, smaller than 100), users can navigate between pages using prev/next buttons, which mainly reduces data load per request.

- However, let's say when a user wants to go to page 501, then ElasticSearch must scan and “skip” (i.e., throwing away) the first 10,000 documents (considering page size is 20) just to get page 501. This could lead to unexpected **performance bottlenecks**, even though it’s devised to enhance performance at first.

- More specifically, this is a problem as currently pagination is implemented in a way that ElasticSearch is being told every time to sort its documents, until “From” using heap sorting algorithm, whenever a user clicks the pagination button. Without **caching**, (which is the case), it can be pretty expensive to the ElasticSearch cluster.

- Using `search_after` could resolve this issue, as it specifies where to start, via giving unique sort fields. In addition, this will cover when a new document is added at the top **online**.

- Currently **errors** are pretty generic and not structured well. When errors are too detailed, there will be a high chance for the sensitive information to be disclosed, and if it’s too general, it’s difficult to catch the pattern even internally. Following could be one of the example of the error customization.

```python
# error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

```

- Unfortunately significant parts of monitoring and testing are missing, although they are critical components of the delivering services.

- In addition, proxy routing (with Codesandbox setup), API response **caching** with appropriate TTL (Time To Live), query optimization or caching.
