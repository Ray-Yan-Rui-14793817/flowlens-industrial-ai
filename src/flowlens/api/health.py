"""Database-backed health endpoint."""

from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.engine import Engine

from flowlens.api.schemas import HealthResponse
from flowlens.config import Settings
from flowlens.db import DatabaseUnavailableError, check_database_connectivity

router = APIRouter()


def get_database_engine(request: Request) -> Engine:
    """Return the application-owned SQLAlchemy engine."""

    return cast(Engine, request.app.state.database_engine)


@router.get("/health", response_model=HealthResponse)
def get_health(
    request: Request,
    response: Response,
    engine: Annotated[Engine, Depends(get_database_engine)],
) -> HealthResponse:
    """Report service health based on real database connectivity."""

    settings = cast(Settings, request.app.state.settings)

    try:
        check_database_connectivity(engine)
    except DatabaseUnavailableError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(
            status="degraded",
            service=settings.service_name,
            database="unavailable",
        )

    return HealthResponse(
        status="ok",
        service=settings.service_name,
        database="ok",
    )
