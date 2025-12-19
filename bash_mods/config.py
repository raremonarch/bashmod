"""Configuration management for bash-mods."""

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
    DEFAULT_GITHUB_USER = "user"
    DEFAULT_GITHUB_REPO = "bashrc-modules"
    DEFAULT_GITHUB_BRANCH = "main"
    DEFAULT_INSTALL_DIR = "~/.bashrc.d"

    def __init__(self):
        """Initialize configuration."""
        self.config_file = Path.home() / ".config" / "bash-mods" / "config.toml"
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                if tomllib is None:
                    # Fallback if tomli not installed
                    return {}
                with open(self.config_file, "rb") as f:
                    return tomllib.load(f)
            except Exception:
                # If config is invalid, return empty dict
                return {}
        return {}

    def save_config(self) -> None:
        """Save configuration to file (not implemented for TOML)."""
        # TOML writing is not commonly needed and requires additional dependencies
        # Users should edit the config file manually
        raise NotImplementedError(
            "Config saving not implemented. Please edit the config file manually at: "
            f"{self.config_file}"
        )

    @property
    def github_user(self) -> str:
        """Get GitHub username."""
        return self._config.get("github_user", self.DEFAULT_GITHUB_USER)

    @github_user.setter
    def github_user(self, value: str) -> None:
        """Set GitHub username."""
        self._config["github_user"] = value

    @property
    def github_repo(self) -> str:
        """Get GitHub repository name."""
        return self._config.get("github_repo", self.DEFAULT_GITHUB_REPO)

    @github_repo.setter
    def github_repo(self, value: str) -> None:
        """Set GitHub repository name."""
        self._config["github_repo"] = value

    @property
    def github_branch(self) -> str:
        """Get GitHub branch name."""
        return self._config.get("github_branch", self.DEFAULT_GITHUB_BRANCH)

    @github_branch.setter
    def github_branch(self, value: str) -> None:
        """Set GitHub branch name."""
        self._config["github_branch"] = value

    @property
    def registry_url(self) -> str:
        """Get registry URL (custom or generated from GitHub settings)."""
        custom_url = self._config.get("registry_url")
        if custom_url:
            return custom_url

        # Generate from GitHub settings
        return (
            f"https://raw.githubusercontent.com/"
            f"{self.github_user}/{self.github_repo}/{self.github_branch}/registry.json"
        )

    @registry_url.setter
    def registry_url(self, value: Optional[str]) -> None:
        """Set custom registry URL (or None to use GitHub settings)."""
        if value:
            self._config["registry_url"] = value
        elif "registry_url" in self._config:
            del self._config["registry_url"]

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
