from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse

from app.config import settings
from app.routers import dreams, health

app = FastAPI(title="Tús API", version="0.1.0")


@app.middleware("http")
async def limit_body_size(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Reject oversized bodies up front (audio upload guard). The client also
    caps duration, but the client is not a trust boundary."""
    content_length = request.headers.get("content-length")
    if content_length is not None and int(content_length) > settings.max_upload_bytes:
        return JSONResponse({"detail": "request body too large"}, status_code=413)
    return await call_next(request)


app.include_router(health.router)
app.include_router(dreams.router)
