"""Response schemas for the Week 1 API contract."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Database-aware service health response."""

    status: Literal["ok", "degraded"]
    service: str
    database: Literal["ok", "unavailable"]
