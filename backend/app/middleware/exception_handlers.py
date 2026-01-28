# backend/app/middleware/exception_handlers.py
"""Global exception handlers for graceful error handling"""

import logging
import traceback
from datetime import datetime
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Setup logger for this module
logger = logging.getLogger("app.exceptions")


class APIError(Exception):
    """Base exception for API errors"""
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


def create_error_response(
    status_code: int,
    message: str,
    details: dict = None,
    path: str = None
) -> JSONResponse:
    """Create a standardized error response"""
    content = {
        "error": True,
        "status_code": status_code,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if path:
        content["path"] = path
    if details:
        content["details"] = details
    
    return JSONResponse(status_code=status_code, content=content)


def setup_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app"""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle custom API errors"""
        logger.warning(f"API Error: {exc.message} | Path: {request.url.path}")
        return create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP {exc.status_code}: {exc.detail} | Path: {request.url.path}")
        return create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            path=request.url.path
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        errors = exc.errors()
        logger.warning(f"Validation Error: {errors} | Path: {request.url.path}")
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            details={"errors": errors},
            path=request.url.path
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        Global exception handler - catches all unhandled exceptions.
        Logs the full traceback and returns a generic error response.
        """
        # Log the full error with traceback
        logger.error(
            f"Unhandled Exception: {type(exc).__name__}: {str(exc)} | Path: {request.url.path}",
            exc_info=True
        )
        
        # Log to file as well
        error_details = {
            "type": type(exc).__name__,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
        logger.error(f"Full error details: {error_details}")
        
        # Return a safe error response (don't expose internal details)
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An internal server error occurred. Please try again later.",
            path=request.url.path
        )
