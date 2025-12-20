"""Core functionality for bashmod."""

from .registry import Registry
from .parser import ShellScriptParser
from .conflicts import ConflictDetector
from .installer import ModuleInstaller

__all__ = ["Registry", "ShellScriptParser", "ConflictDetector", "ModuleInstaller"]
