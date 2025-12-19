"""Shell script parser for extracting aliases, functions, and variables."""

import re
from typing import Set
from bash_mods.models import ModuleExports


class ShellScriptParser:
    """Parse shell scripts to extract definitions."""

    # Regex patterns for bash constructs
    ALIAS_PATTERN = re.compile(r'^\s*alias\s+([a-zA-Z0-9_-]+)=', re.MULTILINE)
    FUNCTION_PATTERN = re.compile(
        r'^\s*(?:function\s+)?([a-zA-Z0-9_-]+)\s*\(\s*\)\s*\{',
        re.MULTILINE
    )
    EXPORT_VAR_PATTERN = re.compile(r'^\s*export\s+([a-zA-Z0-9_]+)=', re.MULTILINE)

    @classmethod
    def parse(cls, script_content: str) -> ModuleExports:
        """Parse a shell script and extract exports."""
        # Remove comments to avoid false positives
        lines = []
        for line in script_content.split('\n'):
            # Remove inline comments but preserve quoted strings
            if '#' in line:
                # Simple approach: remove from # to end of line
                # (doesn't handle # in strings perfectly, but good enough)
                if not ('"' in line or "'" in line):
                    line = line.split('#')[0]
            lines.append(line)

        cleaned_content = '\n'.join(lines)

        aliases = cls._extract_aliases(cleaned_content)
        functions = cls._extract_functions(cleaned_content)
        variables = cls._extract_variables(cleaned_content)

        return ModuleExports(
            aliases=sorted(list(aliases)),
            functions=sorted(list(functions)),
            variables=sorted(list(variables))
        )

    @classmethod
    def _extract_aliases(cls, content: str) -> Set[str]:
        """Extract alias names."""
        return set(cls.ALIAS_PATTERN.findall(content))

    @classmethod
    def _extract_functions(cls, content: str) -> Set[str]:
        """Extract function names."""
        return set(cls.FUNCTION_PATTERN.findall(content))

    @classmethod
    def _extract_variables(cls, content: str) -> Set[str]:
        """Extract exported variable names."""
        return set(cls.EXPORT_VAR_PATTERN.findall(content))
