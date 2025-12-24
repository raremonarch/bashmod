"""Configuration management for bashmod."""

import os
import sys
from pathlib import Path
from typing import Optional

# Use tomllib for Python 3.11+, tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore


class Config:
    """Application configuration."""

    # Default values
    DEFAULT_INSTALL_DIR = "~/.bashrc.d"

    def __init__(self):
        """Initialize configuration."""
        self.config_file = Path.home() / ".config" / "bashmod" / "config.toml"
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                if tomllib is None:
                    # tomli not available
                    self.config_error = (
                        f"Config file found but tomli/tomllib not available"
                    )
                    return {}
                with open(self.config_file, "rb") as f:
                    return tomllib.load(f)
            except Exception as e:
                # Config parsing failed
                self.config_error = f"Could not parse config file: {e}"
                return {}

        # No config file found
        self.config_error = f"Config file not found."
        return {}

    @property
    def has_error(self) -> bool:
        """Check if there's a configuration error."""
        return hasattr(self, "config_error")

    def get_error_message(self) -> str:
        """Get the configuration error message."""
        if not self.has_error:
            return ""

        msg = f"⚠ Configuration Error\n\n{self.config_error}\n\n"
        msg += "To fix:\n"
        msg += "1. Create the config directory:\n"
        msg += f"   mkdir -p {self.config_file.parent}\n\n"
        msg += "2. Copy the example config:\n"
        msg += f"   cp config.example.toml {self.config_file}\n\n"
        msg += "3. Edit with your settings:\n"
        msg += f"   vim {self.config_file}"

        return msg

    def save_config(self) -> None:
        """Save configuration to file (not implemented for TOML)."""
        # TOML writing is not commonly needed and requires additional dependencies
        # Users should edit the config file manually
        raise NotImplementedError(
            "Config saving not implemented. Please edit the config file manually at: "
            f"{self.config_file}"
        )

    @property
    def registries(self) -> list[str]:
        """Get list of registries (URLs or local paths).

        Supports both:
        - New unified format: registries = ["url1", "path1", ...]
        - Legacy format: registry_urls and registry_paths (for backwards compatibility)
        """
        # Check for new unified format first
        if "registries" in self._config:
            return self._config.get("registries", [])

        # Fall back to legacy format
        urls = self._config.get("registry_urls", [])
        paths = self._config.get("registry_paths", [])
        return urls + paths

    @property
    def registry_urls(self) -> list[str]:
        """Get list of registry URLs (HTTP/HTTPS).

        DEPRECATED: Use registries property instead.
        Kept for backwards compatibility.
        """
        # If using new unified format, filter to URLs only
        if "registries" in self._config:
            return [r for r in self.registries if r.startswith(("http://", "https://"))]
        return self._config.get("registry_urls", [])

    @registry_urls.setter
    def registry_urls(self, value: list[str]) -> None:
        """Set registry URLs."""
        self._config["registry_urls"] = value

    @property
    def registry_paths(self) -> list[str]:
        """Get list of local registry paths.

        DEPRECATED: Use registries property instead.
        Kept for backwards compatibility.
        """
        # If using new unified format, filter to non-URLs only
        if "registries" in self._config:
            return [r for r in self.registries if not r.startswith(("http://", "https://"))]
        return self._config.get("registry_paths", [])

    @property
    def install_dir(self) -> Path:
        """Get installation directory."""
        install_path = self._config.get("install_dir", self.DEFAULT_INSTALL_DIR)
        return Path(os.path.expanduser(install_path))

    @install_dir.setter
    def install_dir(self, value: str) -> None:
        """Set installation directory."""
        self._config["install_dir"] = value


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
