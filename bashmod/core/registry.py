"""Module registry management."""

import json
from typing import List, Optional
import httpx

from bashmod.models import Module
from bashmod.config import get_config


class Registry:
    """Manages the module registry from GitHub."""

    def __init__(self, registry_url: Optional[str] = None):
        """Initialize registry with optional custom URL."""
        if registry_url:
            self.registry_url = registry_url
        else:
            # Use registry URL from config
            config = get_config()
            self.registry_url = config.registry_url

        self._modules: List[Module] = []
        self._loaded = False

    async def fetch(self) -> None:
        """Fetch and parse the module registry from GitHub."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.registry_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        self._modules = [Module(**mod) for mod in data.get("modules", [])]
        self._loaded = True

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
        """Search modules by name, description, or category."""
        query_lower = query.lower()
        results = []
        for module in self.get_modules():
            if (
                query_lower in module.name.lower()
                or query_lower in module.description.lower()
                or query_lower in module.category.lower()
                or query_lower in module.id.lower()
            ):
                results.append(module)
        return results

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return sorted(list(set(m.category for m in self.get_modules())))
