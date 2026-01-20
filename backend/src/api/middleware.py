"""
Middleware for FastAPI application.

This module provides logging middleware to track all HTTP requests
and responses for monitoring and debugging purposes.
"""

import logging
import time
from fastapi import FastAPI, Request


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def setup_logging_middleware(app: FastAPI) -> None:
    """
    Setup logging middleware for FastAPI application.

    This middleware logs all incoming requests and outgoing responses
    with timing information for performance monitoring.

    Args:
        app: FastAPI application instance
    """

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Log HTTP requests and responses with timing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response from next handler
        """
        # Log incoming request
        start_time = time.time()
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        response = await call_next(request)

        # Log response with timing
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"for {request.method} {request.url.path} "
            f"({process_time:.3f}s)"
        )

        # Add custom header with processing time
        response.headers["X-Process-Time"] = str(process_time)

        return response
