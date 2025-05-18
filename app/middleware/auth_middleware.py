from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


api_version = 'v1'


class CustomAuthMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow unauthenticated access to specific routes
        allowed_paths = [
            "/openapi.json",
            f"/api/{api_version}/docs",
            f"/api/{api_version}/redoc",
            f"/api/{api_version}/auth/login",
            f"/api/{api_version}/auth/signup",
            f"/api/{api_version}/auth/request-verification-link",
            f"/api/{api_version}/auth/verify",
            f"/api/{api_version}/auth/reset-password",
            f"/api/{api_version}/auth/confirm-reset-password",
        ]

        if any(request.url.path.startswith(path) for path in allowed_paths):
            return await call_next(request)


        if "Authorization" not in request.headers:
            return JSONResponse(
                content={
                    "message": "Not authenticated! Please login again to proceed.",
                },
                status_code=401
            )

        response = await call_next(request)
        return response
