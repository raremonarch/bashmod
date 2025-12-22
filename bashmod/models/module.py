"""Module data models."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ModuleExports:
    """Exports (aliases, functions, variables) defined by a module."""

    aliases: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)


@dataclass
class Module:
    """Represents a bash module from the registry."""

    id: str
    description: str
    version: str
    url: str
    category: str
    dependencies: List[str] = field(default_factory=list)
    exports: Optional[ModuleExports] = None

    def __post_init__(self):
        """Convert exports dict to ModuleExports if needed."""
        if isinstance(self.exports, dict):
            self.exports = ModuleExports(**self.exports)
        elif self.exports is None:
            self.exports = ModuleExports()


@dataclass
class InstalledModule:
    """Represents an installed module with metadata."""

    id: str
    version: str
    installed_path: str
    installed_at: str  # ISO format timestamp
