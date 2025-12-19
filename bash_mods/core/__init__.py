"""Core functionality for bash-mods."""

from .registry import Registry
from .parser import ShellScriptParser
from .conflicts import ConflictDetector
from .installer import ModuleInstaller

__all__ = ["Registry", "ShellScriptParser", "ConflictDetector", "ModuleInstaller"]
