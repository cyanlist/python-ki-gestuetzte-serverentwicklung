"""Pydantic model for the paging information of a response."""

from pydantic import BaseModel

__all__ = ["PageInfoModel"]


class PageInfoModel(BaseModel):
    """Information about the returned page."""

    size: int
    number: int
    total_elements: int
    total_pages: int
