from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from app import auth
from app.config import settings
from app.ratelimit import limiter
from app.routers import dreams, health

app = FastAPI(title="Tús API", version="0.1.0")

app.state.limiter = limiter
# slowapi's handler is typed against its own exception, not bare Exception.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Everything else requires a valid Supabase JWT.
PUBLIC_PATHS = frozenset({"/health", "/docs", "/redoc", "/openapi.json"})


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


@app.middleware("http")
async def authenticate(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Verify the Supabase JWT and stash the user id on request.state.

    Runs as middleware (not just a dependency) so the per-user rate limiter can
    key on the user id before the route executes.
    """
    if request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
        return await call_next(request)

    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return JSONResponse({"detail": "missing bearer token"}, status_code=401)

    try:
        request.state.user_id = auth.verify_token(token)
    except auth.InvalidTokenError:
        return JSONResponse({"detail": "invalid token"}, status_code=401)

    return await call_next(request)


app.include_router(health.router)
app.include_router(dreams.router)
