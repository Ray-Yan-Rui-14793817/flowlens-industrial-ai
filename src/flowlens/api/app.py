"""Canonical FastAPI application and lifecycle."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from flowlens.api.health import router as health_router
from flowlens.config import Settings, get_settings
from flowlens.db import create_database_engine


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FlowLens API without connecting to PostgreSQL."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application_settings = settings or get_settings()
        engine = create_database_engine(application_settings)
        application.state.settings = application_settings
        application.state.database_engine = engine
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(title="FlowLens Industrial AI", lifespan=lifespan)
    application.include_router(health_router)
    return application


app = create_app()
