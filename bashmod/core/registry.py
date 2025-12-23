"""Module registry management."""

import json
import sys
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
import httpx

from bashmod.models import Module
from bashmod.config import get_config


class Registry:
    """Manages the module registry from multiple sources."""

    def __init__(self, registry_urls: Optional[List[str]] = None,
                 registry_paths: Optional[List[str]] = None):
        """Initialize registry with optional custom URLs and paths."""
        if registry_urls is not None or registry_paths is not None:
            self.registry_urls = registry_urls or []
            self.registry_paths = registry_paths or []
        else:
            # Use registry URLs/paths from config
            config = get_config()
            self.registry_urls = config.registry_urls
            self.registry_paths = config.registry_paths

        self._modules: List[Module] = []
        self._loaded = False

    @staticmethod
    def _derive_source_label(source: str) -> str:
        """Derive a human-readable label from a registry source."""
        # Handle local paths
        if not source.startswith(('http://', 'https://')):
            # It's a local path
            path = Path(source).expanduser()
            # Remove registry.json from the end if present
            if path.name == 'registry.json':
                path = path.parent
            return str(path)

        # Handle URLs
        parsed = urlparse(source)

        # Special handling for GitHub
        if 'github.com' in parsed.netloc or 'githubusercontent.com' in parsed.netloc:
            # Extract user/repo from path
            # githubusercontent.com: /user/repo/branch/registry.json
            # github.com: /user/repo/...
            parts = [p for p in parsed.path.split('/') if p]
            if len(parts) >= 2:
                user, repo = parts[0], parts[1]
                return f"gh:{user}/{repo}"
            return parsed.netloc

        # For other URLs, use domain + path (minus registry.json)
        path = parsed.path.rstrip('/')
        if path.endswith('/registry.json'):
            path = path[:-14]  # Remove /registry.json
        elif path.endswith('registry.json'):
            path = path[:-13]  # Remove registry.json

        if path and path != '/':
            return f"{parsed.netloc}{path}"
        return parsed.netloc

    async def _fetch_from_url(self, url: str) -> dict:
        """Fetch registry JSON from a URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()

    def _fetch_from_file(self, path: str) -> dict:
        """Fetch registry JSON from a local file."""
        file_path = Path(path).expanduser()
        with open(file_path, 'r') as f:
            return json.load(f)

    def _parse_registry_data(self, data: dict, source: str) -> List[Module]:
        """Parse and validate registry data from a single source."""
        # Validate registry version
        registry_version = data.get("version", "1.0")
        if registry_version != "1.0":
            raise ValueError(
                f"Unsupported registry version: {registry_version}"
            )

        # Parse modules with validation
        modules = []
        for idx, mod in enumerate(data.get("modules", [])):
            # Validate: reject modules with 'name' field
            if "name" in mod:
                raise ValueError(
                    f"Module at index {idx} (id: {mod.get('id', 'unknown')}) "
                    f"contains invalid 'name' field. "
                    f"The 'name' field is not part of the registry schema. "
                    f"Remove it."
                )
            # Add source label to module data
            mod_with_source = {**mod, "source": source}
            modules.append(Module(**mod_with_source))

        return modules

    async def fetch(self) -> None:
        """Fetch and parse module registries from all configured sources."""
        all_modules = []
        errors = []

        # Fetch from URLs
        for url in self.registry_urls:
            try:
                source_label = self._derive_source_label(url)
                data = await self._fetch_from_url(url)
                modules = self._parse_registry_data(data, source_label)
                all_modules.extend(modules)
            except Exception as e:
                errors.append(f"Failed to load {url}: {e}")

        # Fetch from local paths
        for path in self.registry_paths:
            try:
                source_label = self._derive_source_label(path)
                data = self._fetch_from_file(path)
                modules = self._parse_registry_data(data, source_label)
                all_modules.extend(modules)
            except Exception as e:
                errors.append(f"Failed to load {path}: {e}")

        # If all sources failed, raise an error
        if not all_modules and errors:
            raise RuntimeError(
                f"Failed to load any registries:\n" + "\n".join(errors)
            )

        self._modules = all_modules
        self._loaded = True

        # Log any partial failures (some succeeded, some failed)
        if errors:
            for error in errors:
                print(f"Warning: {error}", file=sys.stderr)

    def get_modules(self) -> List[Module]:
        """Get all available modules."""
        if not self._loaded:
            raise RuntimeError("Registry not loaded. Call fetch() first.")
        return self._modules

    def get_module(self, module_id: str) -> Optional[Module]:
        """Get a specific module by ID."""
        for module in self.get_modules():
            if module.id == module_id:
                return module
        return None

    def search(self, query: str) -> List[Module]:
        """Search modules by ID, description, or category."""
        query_lower = query.lower()
        results = []
        for module in self.get_modules():
            if (
                query_lower in module.id.lower()
                or query_lower in module.description.lower()
                or query_lower in module.category.lower()
            ):
                results.append(module)
        return results

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return sorted(list(set(m.category for m in self.get_modules())))
