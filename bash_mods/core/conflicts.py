"""Conflict detection between modules."""

from typing import Dict, List, Set
from dataclasses import dataclass
from bash_mods.models import Module, ModuleExports


@dataclass
class Conflict:
    """Represents a conflict between modules."""

    name: str  # Name of the conflicting item (alias/function/variable)
    type: str  # "alias", "function", or "variable"
    modules: List[str]  # List of module IDs that define this item


class ConflictDetector:
    """Detect conflicts between modules."""

    @staticmethod
    def detect_conflicts(modules: List[Module]) -> List[Conflict]:
        """Detect all conflicts across a list of modules."""
        conflicts = []

        # Track which modules define each item
        aliases: Dict[str, Set[str]] = {}
        functions: Dict[str, Set[str]] = {}
        variables: Dict[str, Set[str]] = {}

        for module in modules:
            if not module.exports:
                continue

            # Track aliases
            for alias in module.exports.aliases:
                if alias not in aliases:
                    aliases[alias] = set()
                aliases[alias].add(module.id)

            # Track functions
            for func in module.exports.functions:
                if func not in functions:
                    functions[func] = set()
                functions[func].add(module.id)

            # Track variables
            for var in module.exports.variables:
                if var not in variables:
                    variables[var] = set()
                variables[var].add(module.id)

        # Find conflicts (items defined by multiple modules)
        for alias_name, module_ids in aliases.items():
            if len(module_ids) > 1:
                conflicts.append(Conflict(
                    name=alias_name,
                    type="alias",
                    modules=sorted(list(module_ids))
                ))

        for func_name, module_ids in functions.items():
            if len(module_ids) > 1:
                conflicts.append(Conflict(
                    name=func_name,
                    type="function",
                    modules=sorted(list(module_ids))
                ))

        for var_name, module_ids in variables.items():
            if len(module_ids) > 1:
                conflicts.append(Conflict(
                    name=var_name,
                    type="variable",
                    modules=sorted(list(module_ids))
                ))

        return sorted(conflicts, key=lambda c: (c.type, c.name))

    @staticmethod
    def format_conflicts(conflicts: List[Conflict]) -> str:
        """Format conflicts as a human-readable string."""
        if not conflicts:
            return "No conflicts detected."

        lines = [f"Found {len(conflicts)} conflict(s):\n"]
        for conflict in conflicts:
            modules_str = ", ".join(conflict.modules)
            lines.append(f"  • {conflict.type} '{conflict.name}' in: {modules_str}")

        return "\n".join(lines)
