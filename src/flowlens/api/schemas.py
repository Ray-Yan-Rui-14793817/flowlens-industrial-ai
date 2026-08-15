"""Response schemas for the Week 1 API contract."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Database-aware service health response."""

    status: Literal["ok", "degraded"]
    service: Literal["flowlens-api"] = "flowlens-api"
    database: Literal["ok", "unavailable"]
