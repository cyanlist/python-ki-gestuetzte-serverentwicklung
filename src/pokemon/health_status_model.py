"""Pydantic model for the result of a health check."""

from typing import Literal

from pydantic import BaseModel


class HealthStatusModel(BaseModel):
    """Result of a health check."""

    status: Literal["live", "ready", "not_ready"]
