"""Module data models."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ModuleFile:
    """Represents an additional file that is part of a module."""

    path: str  # Relative path within module directory (e.g., "ssh-host-manager/agent.sh")
    url: str   # URL to download the file from


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
    source: str = ""  # Auto-derived label for registry source
    dependencies: List[str] = field(default_factory=list)
    exports: Optional[ModuleExports] = None
    files: List[ModuleFile] = field(default_factory=list)  # Additional files for multi-file modules

    def __post_init__(self):
        """Convert exports dict to ModuleExports if needed."""
        if isinstance(self.exports, dict):
            self.exports = ModuleExports(**self.exports)
        elif self.exports is None:
            self.exports = ModuleExports()

        # Convert files list of dicts to ModuleFile objects if needed
        if self.files and isinstance(self.files[0], dict):
            self.files = [ModuleFile(**f) for f in self.files]


@dataclass
class InstalledModule:
    """Represents an installed module with metadata."""

    id: str
    version: str
    installed_path: str
    installed_at: str  # ISO format timestamp
