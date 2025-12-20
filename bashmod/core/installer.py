"""Module installation and management."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import httpx

from bashmod.models import Module, InstalledModule, ModuleExports
from bashmod.core.parser import ShellScriptParser
from bashmod.config import get_config


class ModuleInstaller:
    """Manages installation and tracking of modules."""

    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize installer with target directory."""
        if install_dir:
            self.install_dir = install_dir
        else:
            # Use install directory from config
            config = get_config()
            self.install_dir = config.install_dir

        self.metadata_file = self.install_dir / ".bashmod-installed.json"
        self._ensure_install_dir()

    def _ensure_install_dir(self) -> None:
        """Ensure installation directory exists."""
        self.install_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self) -> Dict[str, InstalledModule]:
        """Load installed modules metadata."""
        if not self.metadata_file.exists():
            return {}

        with open(self.metadata_file, 'r') as f:
            data = json.load(f)

        return {
            mod_id: InstalledModule(**mod_data)
            for mod_id, mod_data in data.items()
        }

    def _save_metadata(self, metadata: Dict[str, InstalledModule]) -> None:
        """Save installed modules metadata."""
        data = {
            mod_id: {
                'id': mod.id,
                'version': mod.version,
                'installed_path': mod.installed_path,
                'installed_at': mod.installed_at,
            }
            for mod_id, mod in metadata.items()
        }

        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)

    async def install(self, module: Module) -> None:
        """Install a module."""
        # Download module content
        async with httpx.AsyncClient() as client:
            response = await client.get(module.url, timeout=10.0)
            response.raise_for_status()
            content = response.text

        # Determine filename
        filename = f"{module.id}.sh"
        install_path = self.install_dir / filename

        # Write module file
        with open(install_path, 'w') as f:
            f.write(content)

        # Make executable
        install_path.chmod(0o644)

        # Update metadata
        metadata = self._load_metadata()
        metadata[module.id] = InstalledModule(
            id=module.id,
            version=module.version,
            installed_path=str(install_path),
            installed_at=datetime.now().isoformat()
        )
        self._save_metadata(metadata)

    def uninstall(self, module_id: str) -> bool:
        """Uninstall a module. Returns True if successful."""
        metadata = self._load_metadata()

        if module_id not in metadata:
            return False

        # Remove file
        installed_module = metadata[module_id]
        install_path = Path(installed_module.installed_path)
        if install_path.exists():
            install_path.unlink()

        # Update metadata
        del metadata[module_id]
        self._save_metadata(metadata)
        return True

    def get_installed_modules(self) -> List[InstalledModule]:
        """Get list of all installed modules."""
        metadata = self._load_metadata()
        return list(metadata.values())

    def is_installed(self, module_id: str) -> bool:
        """Check if a module is installed."""
        metadata = self._load_metadata()
        return module_id in metadata

    def get_installed_version(self, module_id: str) -> Optional[str]:
        """Get installed version of a module, or None if not installed."""
        metadata = self._load_metadata()
        if module_id in metadata:
            return metadata[module_id].version
        return None

    def scan_existing_modules(self) -> Dict[str, ModuleExports]:
        """Scan existing modules in install directory and extract exports."""
        exports_map = {}

        if not self.install_dir.exists():
            return exports_map

        for filepath in self.install_dir.glob("*.sh"):
            # Skip metadata file
            if filepath.name.startswith('.'):
                continue

            try:
                with open(filepath, 'r') as f:
                    content = f.read()

                exports = ShellScriptParser.parse(content)
                # Use filename without extension as module ID
                module_id = filepath.stem
                exports_map[module_id] = exports
            except Exception:
                # Skip files that can't be parsed
                continue

        return exports_map
