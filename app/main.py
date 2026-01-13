"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import setup_logging, get_logger
from app.infrastructure.db.session import init_db, close_db
from app.presentation.api.v1.router import api_router
from app.presentation.middleware.request_id import RequestIDMiddleware, RateLimitMiddleware
from app.presentation.exception_handlers import (
    app_error_handler,
    validation_error_handler,
    generic_error_handler,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    setup_logging()
    await init_db()
    
    # Initialize cache
    from app.core.cache import init_cache, shutdown_cache
    await init_cache()
    
    # Start price stream if enabled
    if settings.ENABLE_PRICE_STREAM:
        try:
            from app.infrastructure.streaming.price_stream import price_stream_manager
            await price_stream_manager.connect(market="HOSE")
            logger.info("Price stream started")
        except Exception as e:
            logger.warning(f"Failed to start price stream: {e}")

    # Start scheduler if enabled
    if settings.ENABLE_SCHEDULER:
        try:
            from app.infrastructure.scheduler import start_scheduler
            start_scheduler()
            logger.info("Scheduler started")
        except Exception as e:
            logger.warning(f"Failed to start scheduler: {e}")
    
    yield
    
    # Stop price stream
    if settings.ENABLE_PRICE_STREAM:
        try:
            from app.infrastructure.streaming.price_stream import price_stream_manager
            await price_stream_manager.disconnect()
            logger.info("Price stream stopped")
        except Exception as e:
            logger.warning(f"Error stopping price stream: {e}")

    # Stop scheduler
    if settings.ENABLE_SCHEDULER:
        try:
            from app.infrastructure.scheduler import shutdown_scheduler
            shutdown_scheduler()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.warning(f"Error stopping scheduler: {e}")
    
    # Shutdown cache
    await shutdown_cache()
    
    await close_db()


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Add CORS middleware
    cors_kwargs = {
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    # Use regex for wildcard subdomains if configured
    if settings.CORS_ORIGIN_REGEX:
        cors_kwargs["allow_origin_regex"] = settings.CORS_ORIGIN_REGEX
    else:
        cors_kwargs["allow_origins"] = settings.CORS_ORIGINS_LIST

    app.add_middleware(CORSMiddleware, **cors_kwargs)
    
    # Add middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Add exception handlers
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)
    
    # Include routers
    app.include_router(api_router)
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}
    
    # Serve test realtime page
    @app.get("/test-realtime", tags=["Test"], include_in_schema=False)
    async def test_realtime_page():
        """Serve the realtime test HTML page."""
        static_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "static", "test_realtime.html"
        )
        return FileResponse(static_path, media_type="text/html")
    
    return app


app = create_app()
