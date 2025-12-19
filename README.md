# bash-mods

A TUI (Text User Interface) package manager for modular bash configurations. Easily discover, install, and manage bashrc.d modules from a curated registry.

![bash-mods demo](https://via.placeholder.com/800x400?text=bash-mods+TUI+Demo)

## Features

- 🔍 **Browse & Search** - Interactive TUI to browse available modules
- 📦 **Easy Installation** - One-click install to `~/.bashrc.d/`
- ⚠️ **Conflict Detection** - Automatically detects duplicate aliases, functions, and variables
- 🔄 **Version Management** - Track installed versions and available updates
- 🎨 **Categories** - Modules organized by category (git, docker, python, etc.)
- ⌨️ **Keyboard-Driven** - Fast navigation with vim-style keybindings

## Installation

### Using pipx (Recommended)

```bash
pipx install git+https://github.com/user/bash-mods.git
```

### Using pip

```bash
pip install git+https://github.com/user/bash-mods.git
```

### Development Installation

```bash
git clone https://github.com/user/bash-mods.git
cd bash-mods
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Bash Wrapper (Optional)

For easy access, add the bash wrapper to your PATH:

```bash
# Add to ~/.bashrc or ~/.bash_profile
export PATH="$PATH:/path/to/bash-mods/bin"
```

Now you can run `bash-mods` from anywhere, even in development mode.

## Usage

### Launch the TUI

```bash
bash-mods
```

Or if installed via pipx/pip:

```bash
python -m bash_mods
```

### Development Mode

Run with `--dev` to enable Textual devtools and see detailed error messages:

```bash
bash-mods --dev
# or from the project directory
./bin/bash-mods --dev
```

This is useful for debugging issues or developing new features.

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑/↓` | Navigate modules |
| `Enter` | View module details |
| `Tab` | Switch focus |
| `/` | Focus search |
| `f` | Open category filter menu |
| `h` | Show help |
| `Ctrl+q` | Quit |
| `Ctrl+\` | Command palette (refresh, check conflicts) |

### Filtering by Category

Press `f` to open the category filter menu. Select a category to filter, or choose "All Categories" to clear the filter.

The active category filter is shown in the footer (e.g., `category: development`). You can search within the filtered category by typing in the search box.

### Module Details Screen

- **`i`** - Install module (or press the Install button)
- **`Esc`** - Back to module list

### Configuration

bash-mods uses a configuration file at `~/.config/bash-mods/config.toml`. You can customize:

- **GitHub Repository** - Where to fetch the registry from
- **Registry URL** - Override with a custom registry URL
- **Install Directory** - Where modules are installed (default: `~/.bashrc.d`)

Copy the example config:

```bash
mkdir -p ~/.config/bash-mods
cp config.example.toml ~/.config/bash-mods/config.toml
# Edit the file to customize your settings
```

Example config:

```toml
# GitHub repository settings
github_user = "your-github-username"
github_repo = "bashrc-modules"
github_branch = "main"

# Installation directory
install_dir = "~/.bashrc.d"

# Optional: custom registry URL
# registry_url = "https://example.com/custom-registry.json"
```

You can also override the registry URL at runtime:

```bash
bash-mods --registry-url https://example.com/my-registry.json
```

## How It Works

1. **Module Registry** - Modules are defined in a JSON registry hosted on GitHub
2. **Installation** - Modules are downloaded to `~/.bashrc.d/` and tracked in `.bash-mods-installed.json`
3. **Auto-Loading** - Your `~/.bashrc` should source all files in `~/.bashrc.d/`:

```bash
# Add to ~/.bashrc if not already present
if [ -d ~/.bashrc.d ]; then
    for rc in ~/.bashrc.d/*; do
        if [ -f "$rc" ]; then
            . "$rc"
        fi
    done
fi
unset rc
```

4. **Conflict Detection** - bash-mods scans all installed modules for duplicate definitions

## Creating a Module Registry

Create a `registry.json` file with this format:

```json
{
  "version": "1.0",
  "modules": [
    {
      "id": "git-helpers",
      "name": "Git Helpers",
      "description": "Useful git aliases and functions",
      "version": "1.2.0",
      "url": "https://raw.githubusercontent.com/user/bashrc-modules/main/git.sh",
      "category": "version-control",
      "dependencies": [],
      "exports": {
        "aliases": ["gst", "gco", "glog"],
        "functions": ["git-clone-all", "git-del-branch"],
        "variables": []
      }
    }
  ]
}
```

### Module Fields

- **id** - Unique identifier (used for filenames)
- **name** - Display name
- **description** - Short description of what the module does
- **version** - Semantic version (MAJOR.MINOR.PATCH)
- **url** - Direct download URL for the module script
- **category** - Category for organization (git, docker, python, etc.)
- **dependencies** - Array of module IDs this depends on (optional, not enforced yet)
- **exports** - What the module defines (helps with conflict detection)

## Conflict Detection

bash-mods automatically detects conflicts between modules:

- **On Startup** - Scans all installed modules
- **After Install** - Checks if new module conflicts with existing ones

Conflicts are shown in a warning panel at the top of the TUI. Press `c` to see detailed conflict information.

### Example Conflict

```
⚠ 2 conflict(s) detected

  • alias 'gs' in: git-helpers, git-shortcuts
  • function 'docker-clean' in: docker-utils, system-cleanup
```

You can choose to keep both modules (last one loaded wins) or uninstall one to resolve the conflict.

## Project Structure

```
bash-mods/
├── bash_mods/           # Main package
│   ├── core/            # Core logic
│   │   ├── registry.py  # Registry management
│   │   ├── installer.py # Module installation
│   │   ├── parser.py    # Shell script parsing
│   │   └── conflicts.py # Conflict detection
│   ├── models/          # Data models
│   │   └── module.py    # Module definitions
│   ├── tui/             # TUI interface
│   │   └── app.py       # Textual app
│   └── __main__.py      # CLI entry point
├── bin/                 # Bash wrapper
│   └── bash-mods        # Hybrid bash/python launcher
├── tests/               # Test suite
├── pyproject.toml       # Python project config
└── README.md            # This file
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Roadmap

- [ ] Dependency resolution and enforcement
- [ ] Module update command
- [ ] Export installed modules list
- [ ] Import/backup module configurations
- [ ] Community module submission workflow
- [ ] Integration tests with real bash execution

## Credits

Built with:
- [Textual](https://textual.textualize.io/) - Modern TUI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [httpx](https://www.python-httpx.org/) - HTTP client
