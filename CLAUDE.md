# Claude Code Context for bash-mods

## Project Overview

bash-mods is a TUI (Text User Interface) application for discovering, installing, and managing modular bash configuration files (bashrc.d modules). It provides a package manager-like experience for shell configurations.

## Purpose

Replace manual bashrc module management with a searchable, installable module system:
- Browse available modules from a GitHub repository
- Search and filter modules by category/keyword
- Install/uninstall modules to `~/.bashrc.d/`
- Detect conflicts between modules (duplicate aliases, functions, variables)
- Version tracking for updates
- Clean, interactive terminal interface

## Architecture

### Components

1. **TUI Interface** - Interactive terminal UI for browsing and managing modules (Textual-based)
2. **Module Registry** - JSON manifest of available modules (GitHub-hosted)
3. **Conflict Detector** - Scans modules for duplicate definitions
4. **Shell Script Parser** - Extracts aliases, functions, and exported variables from bash scripts
5. **Module Installer** - Downloads and manages modules in `~/.bashrc.d/`

### Technology Stack

- **Language**: Python 3.8+
- **TUI Framework**: [Textual](https://textual.textualize.io/) - Modern Python TUI framework
- **HTTP**: `httpx` for async downloading of modules
- **Parsing**: Regex-based shell script parsing to detect aliases/functions/variables

### Hybrid Approach (Python + Bash)

The project uses a **hybrid approach** for maximum usability:

- **Python core** - Robust parsing, conflict detection, and beautiful TUI
- **Bash wrapper** ([bin/bash-mods](bin/bash-mods)) - Automatically detects if bash-mods is:
  - Installed via `pipx` (runs the installed command)
  - Running from source in a venv (activates venv if needed)
  - Not installed (provides helpful installation instructions)

This gives the best of both worlds: Python's power with bash-like convenience.

### Module Registry Format

Modules are described in a JSON manifest (`registry.json`):

```json
{
  "version": "1.0",
  "modules": [
    {
      "id": "git-helpers",
      "name": "Git Helpers",
      "description": "Git aliases and clone helpers for multiple remotes",
      "version": "1.0.0",
      "url": "https://raw.githubusercontent.com/user/bashrc-modules/main/git.sh",
      "category": "version-control",
      "dependencies": ["ssh-agent"],
      "exports": {
        "aliases": ["gitaddcommit"],
        "functions": ["ssh_load_key_for_url", "clone-eis", "clone-daevski", "git-del-branch"],
        "variables": []
      }
    }
  ]
}
```

See [example-registry.json](example-registry.json) for a complete example.

### Actual File Structure

```
~/Downloads/code/bash-mods/
├── CLAUDE.md                      # This file
├── README.md                      # User-facing documentation
├── pyproject.toml                 # Python project config (setuptools)
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Dev dependencies
├── example-registry.json          # Example module registry
├── .gitignore                     # Git ignore patterns
├── bin/
│   └── bash-mods                  # Bash wrapper script (hybrid launcher)
├── bash_mods/                     # Main Python package
│   ├── __init__.py                # Package init
│   ├── __main__.py                # CLI entry point
│   ├── core/                      # Core logic
│   │   ├── __init__.py
│   │   ├── registry.py            # Fetch and parse module registry from GitHub
│   │   ├── installer.py           # Install/uninstall modules
│   │   ├── conflicts.py           # Conflict detection
│   │   └── parser.py              # Shell script parser (regex-based)
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   └── module.py              # Module, ModuleExports, InstalledModule
│   └── tui/                       # TUI components
│       ├── __init__.py
│       └── app.py                 # Main Textual app + detail screen
└── tests/                         # Test suite (empty for now)
```

## Key Design Decisions

### Conflict Detection

- **What to detect**: Duplicate aliases, functions, exported environment variables
- **When to check**: On startup (scans all installed modules) and after each install
- **How to handle**: Show warning panel at top of TUI with count, press 'c' for details
- **User choice**: User sees conflicts but can choose to keep both modules (bash "last one wins" behavior)

Implementation: [bash_mods/core/conflicts.py](bash_mods/core/conflicts.py)

### Module Versioning

- Semantic versioning (MAJOR.MINOR.PATCH)
- Installed version tracked in `~/.bashrc.d/.bash-mods-installed.json`
- Available version comes from registry
- Update indicator in TUI: `↑` symbol when update available

### Shell Script Parsing

Located in [bash_mods/core/parser.py](bash_mods/core/parser.py).

Uses regex patterns to extract:
- **Aliases**: `alias name=...`
- **Functions**: `function name() {` or `name() {`
- **Exported vars**: `export VAR=...`

Limitations:
- Doesn't handle all edge cases (complex quoting, heredocs, etc.)
- Good enough for typical bashrc modules
- Consider using `shellcheck` or proper bash AST parsing for production

### Dependency Management

- Registry can declare dependencies in the `dependencies` field
- **Not enforced in v1** - shown in module details but not required
- Future: Add topological sorting and auto-install dependencies

### Installation Location

- Default: `~/.bashrc.d/`
- Modules saved as `{module-id}.sh`
- Metadata tracked in `~/.bashrc.d/.bash-mods-installed.json`
- User's `~/.bashrc` should source all files in `~/.bashrc.d/`

### Registry Source

- Default URL: Set in [bash_mods/core/registry.py](bash_mods/core/registry.py#L11)
- Can be overridden with `--registry-url` flag
- **TODO**: Update default URL to actual GitHub repo

## Development Workflow

### Setup Development Environment

```bash
cd ~/Downloads/code/bash-mods
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Running the App

Using the bash wrapper (recommended):
```bash
./bin/bash-mods
```

Or directly:
```bash
python -m bash_mods
```

With custom registry:
```bash
bash-mods --registry-url https://example.com/registry.json
```

### Installing for Production

Using pipx (recommended):
```bash
pipx install git+https://github.com/user/bash-mods.git
```

Using pip:
```bash
pip install git+https://github.com/user/bash-mods.git
```

### Testing

```bash
pytest tests/
```

(No tests implemented yet)

## TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑/↓` | Navigate module list |
| `Enter` | View module details |
| `/` | Focus search box |
| `r` | Refresh registry from GitHub |
| `c` | Show detailed conflict information |
| `q` | Quit |

In module detail screen:
- `i` or Install button - Install module
- Uninstall button - Remove installed module
- `Esc` or Back button - Return to list

## Current Status

- **Phase**: Initial implementation complete
- **Status**: Functional prototype ready for testing
- **Completed**:
  - ✅ Python project structure
  - ✅ Core data models
  - ✅ Module registry fetching (async with httpx)
  - ✅ Shell script parser (regex-based)
  - ✅ Conflict detector
  - ✅ Module installer/uninstaller
  - ✅ Textual TUI with search, browse, install
  - ✅ Bash wrapper for hybrid approach (auto-setup venv)
  - ✅ TOML configuration system
  - ✅ README and documentation

## Next Steps

1. **Create actual module registry** - Host `registry.json` on GitHub with real modules
2. **Test with existing modules** - Use user's `~/.bashrc.d/` modules as test data
3. **Update default registry URL** - Point to actual GitHub repo
4. **Add tests** - Unit tests for parser, conflict detector, installer
5. **Improve parser** - Handle more edge cases or use proper AST parsing
6. **Add dependency resolution** - Auto-install required dependencies
7. **Module updates** - Add command to update installed modules to latest versions
8. **Error handling** - Better error messages for network failures, malformed modules

## Notes for Future Sessions

### Configuration

bash-mods uses a TOML config file at `~/.config/bash-mods/config.toml`:
- GitHub user, repo, branch (used to construct registry URL)
- Custom registry URL (overrides GitHub settings)
- Install directory (default: `~/.bashrc.d`)

Copy [config.example.toml](config.example.toml) to `~/.config/bash-mods/config.toml` and customize.

The config is loaded via [bash_mods/config.py](bash_mods/config.py) which:
- Uses `tomllib` (Python 3.11+) or `tomli` (older versions)
- Provides sensible defaults if config doesn't exist
- Auto-generates registry URL from GitHub settings

### Registry Setup

To use this with real modules:
1. Create a GitHub repo for module registry
2. Add bash module files (`.sh`) to repo
3. Create `registry.json` manifest
4. Update `~/.config/bash-mods/config.toml` with your GitHub username/repo

### Parser Improvements

Current parser is regex-based and has limitations:
- Doesn't handle heredocs, complex quoting, or multi-line definitions well
- Could use `bashlex` Python library for proper AST parsing
- Or shell out to `bash -n` for syntax validation

### Module Export Detection

The registry requires manual `exports` field. Could be automated:
1. Download module
2. Parse with ShellScriptParser
3. Auto-populate exports in registry
4. Reduces manual work for registry maintainers

### Conflict Resolution

Current approach shows conflicts but doesn't prevent installation. Future options:
- Block installation if conflicts exist (with override flag)
- Allow user to choose which module "wins"
- Namespace modules (prefix aliases/functions)

### Testing the TUI

To test the TUI without a real registry:
1. Use `example-registry.json` with file:// URLs
2. Or create a local HTTP server: `python -m http.server`
3. Point registry at `http://localhost:8000/registry.json`

### Integration with Existing Modules

User has existing modules in `~/.bashrc.d/`:
- audio-switching.sh
- aws.sh
- docker.sh
- gh-cli-tool.sh
- git.sh
- openssl_file_encryption.sh
- pyenv.sh
- python.sh
- ssh-agent.sh
- system.sh

These can be parsed and added to a personal registry for testing.
