"""
Exception handling and error responses for BioNexus API
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BioNexusException(Exception):
    """Base exception for BioNexus application"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "BIONEXUS_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionError(BioNexusException):
    """Raised when database connection fails"""
    
    def __init__(self, message: str = "Database connection failed", details: Dict[str, Any] = None):
        super().__init__(message, "DATABASE_CONNECTION_ERROR", details)


class ProcessingError(BioNexusException):
    """Raised when document processing fails"""
    
    def __init__(self, message: str = "Document processing failed", details: Dict[str, Any] = None):
        super().__init__(message, "PROCESSING_ERROR", details)


class SearchError(BioNexusException):
    """Raised when search operation fails"""
    
    def __init__(self, message: str = "Search operation failed", details: Dict[str, Any] = None):
        super().__init__(message, "SEARCH_ERROR", details)


class ValidationError(BioNexusException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str = "Input validation failed", details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


async def bionexus_exception_handler(request: Request, exc: BioNexusException) -> JSONResponse:
    """Handle BioNexus application exceptions"""
    
    logger.error(
        f"BioNexus exception: {exc.error_code} - {exc.message}",
        extra={"details": exc.details, "path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "path": str(request.url.path),
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors(),
            "path": str(request.url.path),
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    
    # Log the full traceback for debugging
    logger.error(
        f"Unexpected exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
        }
    )


# Error response templates
def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: Dict[str, Any] = None
) -> JSONResponse:
    """Create standardized error response"""
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "error_code": error_code,
            "message": message,
            "details": details or {},
            "timestamp": str(datetime.utcnow()),
        }
    )


def create_success_response(
    data: Any = None,
    message: str = "Success",
    meta: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create standardized success response"""
    
    response = {
        "error": False,
        "message": message,
    }
    
    if data is not None:
        response["data"] = data
    
    if meta:
        response["meta"] = meta
    
    return response