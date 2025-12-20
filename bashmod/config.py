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
    DEFAULT_GITHUB_USER = "user"
    DEFAULT_GITHUB_REPO = "bashrc-modules"
    DEFAULT_GITHUB_BRANCH = "main"
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
