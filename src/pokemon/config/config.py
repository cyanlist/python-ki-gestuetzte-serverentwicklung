"""Read the configuration from the TOML file."""

from importlib.resources import files
from tomllib import load
from typing import Any, Final

__all__ = ["app_config", "resources_path"]

resources_path: Final = "pokemon.config.resources"
"""Package that contains the resource files, e.g. `app.toml`."""

_config_file: Final = files(resources_path) / "app.toml"

with _config_file.open(mode="rb") as reader:
    app_config: Final[dict[str, Any]] = load(reader)
"""The content of `app.toml` as a dictionary. It is read once, at the first import."""
