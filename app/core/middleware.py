import uuid
import time
from fastapi import Request, Response, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog
from structlog.contextvars import clear_contextvars, bind_contextvars
from app.shared.responses.envelope import wrap_response
from app.shared.exceptions.domain_exceptions import DomainException

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        clear_contextvars()
        
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID") or request_id
        
        bind_contextvars(
            request_id=request_id,
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method
        )
        
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            logger.info("Request completed", status_code=response.status_code, duration_ms=round(process_time * 1000, 2))
            
            # Security Headers - skip strict CSP for swagger docs
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Content-Type-Options"] = "nosniff"
            
            if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                response.headers["Content-Security-Policy"] = "default-src 'self'"
            
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.exception("Request unhandled exception", duration_ms=round(process_time * 1000, 2), error=str(e))
            
            if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
                raise e

            status_code = 500
            error_code = "INTERNAL_SERVER_ERROR"
            message = "An unexpected server error occurred."
            
            response = wrap_response(
                success=False,
                message=message,
                request_id=request_id,
                errors={"code": error_code},
                status_code=status_code
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            
            return response

def setup_exception_handlers(app: FastAPI):
    """Registers global exception handlers for the application."""
    
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        request_id = getattr(request.state, "request_id", "")
        status_code = 400
        if exc.code == "NOT_FOUND":
            status_code = 404
        elif exc.code in ("UNAUTHENTICATED", "TOKEN_EXPIRED", "TOKEN_REVOKED"):
            status_code = 401
        elif exc.code == "UNAUTHORIZED":
            status_code = 403
            
        logger.warn("Domain exception raised", code=exc.code, message=exc.message)
        errors = getattr(exc, "errors", None) or {"code": exc.code}
        return wrap_response(
            success=False,
            message=exc.message,
            request_id=request_id,
            errors=errors,
            status_code=status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", "")
        logger.warn("Validation error occurred", errors=exc.errors())
        return wrap_response(
            success=False,
            message="Validation failed",
            request_id=request_id,
            errors={"code": "VALIDATION_ERROR", "details": exc.errors()},
            status_code=422
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            # Do not intercept HTTP exceptions for Swagger endpoints
            from fastapi.responses import HTMLResponse, JSONResponse
            if isinstance(exc.detail, dict):
                return JSONResponse(status_code=exc.status_code, content=exc.detail)
            return HTMLResponse(status_code=exc.status_code, content=str(exc.detail))

        request_id = getattr(request.state, "request_id", "")
        logger.warn("HTTP exception raised", status_code=exc.status_code, detail=exc.detail)
        return wrap_response(
            success=False,
            message=exc.detail,
            request_id=request_id,
            errors={"code": f"HTTP_{exc.status_code}"},
            status_code=exc.status_code
        )
