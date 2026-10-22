"""Constants for the REST interface."""

from typing import Final

__all__ = ["ETAG", "IF_NONE_MATCH"]

ETAG: Final = "ETag"
"""Name of the response header with the version of a resource."""

IF_NONE_MATCH: Final = "If-None-Match"
"""Name of the request header for conditional GET requests."""
