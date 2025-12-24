"""Main Textual application."""

from typing import List

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, DataTable, Input, Static, Button, OptionList
)
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual.screen import Screen
from textual import on

from bashmod.core import Registry, ModuleInstaller
from bashmod.models import Module
from bashmod.config import get_config


class CategoryFilterScreen(Screen):
    """Screen for selecting category filter."""

    CSS = """
    CategoryFilterScreen {
        align: center middle;
    }

    CategoryFilterScreen > Vertical {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 1;
    }

    .filter-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #category-options {
        height: auto;
        max-height: 20;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "cancel"),
    ]

    def __init__(self, categories: list[str], current_filter: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = categories
        self.current_filter = current_filter

    def compose(self) -> ComposeResult:
        """Compose the category selection screen."""
        yield Header()
        with Vertical():
            yield Static("Select Category Filter", classes="filter-title")
            option_list = OptionList(id="category-options")
            yield option_list
        yield Footer()

    def on_mount(self) -> None:
        """Populate the option list."""
        option_list = self.query_one(OptionList)

        # Add "All" option
        option_list.add_option(Option("All Categories", id="all"))

        # Add each category
        for cat in self.categories:
            option_list.add_option(Option(cat, id=cat))

        # Highlight current selection
        if self.current_filter:
            option_list.highlighted = self.categories.index(self.current_filter) + 1
        else:
            option_list.highlighted = 0

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle category selection."""
        selected_id = event.option_id
        if selected_id == "all":
            self.dismiss(None)
        else:
            self.dismiss(selected_id)

    def action_dismiss(self) -> None:
        """Cancel selection."""
        self.dismiss(None)


class ModuleDetailScreen(Screen):
    """Screen showing details of a selected module."""

    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
        Binding("i", "install", "Install"),
    ]

    def __init__(self, module: Module, installer: ModuleInstaller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.module = module
        self.installer = installer

    def compose(self) -> ComposeResult:
        """Compose the detail view."""
        is_installed = self.installer.is_installed(self.module.id)
        installed_version = self.installer.get_installed_version(self.module.id)

        status = "✓ Installed" if is_installed else "Not installed"
        if is_installed and installed_version != self.module.version:
            status += f" (v{installed_version}, update available: v{self.module.version})"

        yield Header()
        with Vertical():
            yield Static(f"[bold]{self.module.id}[/bold]", classes="detail-title")
            yield Static(f"Version: {self.module.version}", classes="detail-field")
            yield Static(f"Category: {self.module.category}", classes="detail-field")
            yield Static(f"Status: {status}", classes="detail-field")
            yield Static(f"\n{self.module.description}", classes="detail-description")

            if self.module.exports:
                exports_text = []
                if self.module.exports.aliases:
                    exports_text.append(f"Aliases: {', '.join(self.module.exports.aliases)}")
                if self.module.exports.functions:
                    exports_text.append(f"Functions: {', '.join(self.module.exports.functions)}")
                if self.module.exports.variables:
                    exports_text.append(f"Variables: {', '.join(self.module.exports.variables)}")

                if exports_text:
                    yield Static("\n[bold]Exports:[/bold]", classes="detail-section")
                    for line in exports_text:
                        yield Static(f"  • {line}", classes="detail-list")

            if self.module.dependencies:
                yield Static("\n[bold]Dependencies:[/bold]", classes="detail-section")
                for dep in self.module.dependencies:
                    yield Static(f"  • {dep}", classes="detail-list")

            with Horizontal(classes="button-bar"):
                if is_installed:
                    yield Button("Uninstall", id="uninstall-btn", variant="error")
                else:
                    yield Button("Install", id="install-btn", variant="primary")
                yield Button("Back", id="back-btn")

        yield Footer()

    def action_dismiss(self) -> None:
        """Go back to main screen."""
        self.app.pop_screen()

    async def action_install(self) -> None:
        """Install the module."""
        if not self.installer.is_installed(self.module.id):
            await self.installer.install(self.module)
            self.app.pop_screen()

    @on(Button.Pressed, "#install-btn")
    async def handle_install(self) -> None:
        """Handle install button press."""
        await self.installer.install(self.module)
        self.notify(f"Installed {self.module.id}")
        self.dismiss(True)  # Signal that refresh is needed

    @on(Button.Pressed, "#uninstall-btn")
    async def handle_uninstall(self) -> None:
        """Handle uninstall button press."""
        self.installer.uninstall(self.module.id)
        self.notify(f"Uninstalled {self.module.id}")
        self.dismiss(True)  # Signal that refresh is needed

    @on(Button.Pressed, "#back-btn")
    def handle_back(self) -> None:
        """Handle back button press."""
        self.app.pop_screen()


class BashMod(App):
    """Main application for bashmod TUI."""

    CSS = """
    Screen {
        background: $surface;
    }

    #search-input {
        dock: top;
        margin: 1;
    }

    #config-error-panel {
        dock: top;
        height: auto;
        background: $error;
        color: $text;
        padding: 1;
        margin: 0 1;
    }

    #conflicts-panel {
        dock: top;
        height: auto;
        background: $warning;
        color: $text;
        padding: 1;
        margin: 0 1;
    }

    DataTable {
        height: 1fr;
    }

    .detail-title {
        margin: 1 0;
        text-style: bold;
    }

    .detail-field {
        margin: 0 0 0 2;
    }

    .detail-description {
        margin: 1 2;
    }

    .detail-section {
        margin: 1 0 0 2;
    }

    .detail-list {
        margin: 0 0 0 4;
    }

    .button-bar {
        margin: 2;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "quit", show=True, priority=True),
        Binding("h", "help", "help", show=True, priority=True),
        Binding("r", "refresh", "Refresh registry from GitHub", show=False),
        Binding("c", "check_conflicts", "Check Conflicts", show=False),
        Binding("/", "focus_search", "search", show=True, priority=True),
        Binding("f", "filter_category", "filter category", show=True, priority=True),
    ]

    def __init__(self, registry_urls: List[str] = None,
                 registry_paths: List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry = Registry(registry_urls, registry_paths)
        self.installer = ModuleInstaller()
        self.current_modules = []
        self.current_category_filter = None

    def compose(self) -> ComposeResult:
        """Compose the main UI."""
        yield Header()
        yield Input(placeholder="Search modules...", id="search-input")
        yield Static("", id="config-error-panel")
        yield Static("", id="conflicts-panel")
        yield DataTable(id="modules-table")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the app on mount."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "Status", "ID", "Version", "Source", "Category", "Description"
        )

        # Hide panels initially
        config_error_panel = self.query_one("#config-error-panel")
        config_error_panel.display = False
        conflicts_panel = self.query_one("#conflicts-panel")
        conflicts_panel.display = False

        # Check for config errors
        config = get_config()
        if config.has_error:
            error_msg = config.get_error_message()
            config_error_panel.update(error_msg)
            config_error_panel.display = True
            # Don't try to load registry if config is broken
            return

        # Set initial focus to table (not search)
        table.focus()

        # Load registry
        self.notify("Loading module registry...")
        try:
            await self.registry.fetch()
            self.current_modules = self.registry.get_modules()
            self._update_table()
            await self._check_conflicts()
        except Exception as e:
            self.notify(f"Error loading registry: {e}", severity="error")
            # Keep current_modules as empty list so the app doesn't crash

    def _update_table(self) -> None:
        """Update the modules table."""
        table = self.query_one(DataTable)
        table.clear()

        # Sort modules by ID first, then by version
        sorted_modules = sorted(
            self.current_modules,
            key=lambda m: (m.id, m.version)
        )

        for module in sorted_modules:
            is_installed = self.installer.is_installed(module.id)
            installed_version = self.installer.get_installed_version(module.id)

            status = "✓" if is_installed else " "
            if is_installed and installed_version != module.version:
                status = "↑"  # Update available

            # Create unique key: source|id|version (using | since source may contain :)
            unique_key = f"{module.source}|{module.id}|{module.version}"

            # Truncate description if too long
            desc = module.description
            if len(desc) > 50:
                desc = desc[:50] + "..."

            table.add_row(
                status,
                module.id,
                module.version,
                module.source,
                module.category,
                desc,
                key=unique_key
            )

    async def _check_conflicts(self) -> None:
        """Check for conflicts and update the conflicts panel."""
        conflicts_panel = self.query_one("#conflicts-panel")

        # Skip if registry not loaded
        if not self.registry._loaded:
            conflicts_panel.display = False
            return

        # Get all installed module IDs
        installed_ids = {m.id for m in self.installer.get_installed_modules()}

        # Get corresponding Module objects
        installed_modules = [
            m for m in self.registry.get_modules()
            if m.id in installed_ids
        ]

        # Detect conflicts
        from bashmod.core.conflicts import ConflictDetector
        conflicts = ConflictDetector.detect_conflicts(installed_modules)

        # Update panel
        if conflicts:
            conflict_text = f"⚠ {len(conflicts)} conflict(s) detected | Press 'c' for details"
            conflicts_panel.update(conflict_text)
            conflicts_panel.display = True
        else:
            conflicts_panel.display = False

    @on(Input.Changed, "#search-input")
    def handle_search(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        query = event.value.strip()

        # Get base modules (filtered by category if active)
        if self.current_category_filter:
            base_modules = [
                m for m in self.registry.get_modules()
                if m.category == self.current_category_filter
            ]
        else:
            base_modules = self.registry.get_modules()

        # Apply search query if present
        if query:
            query_lower = query.lower()
            self.current_modules = [
                m for m in base_modules
                if (query_lower in m.id.lower()
                    or query_lower in m.description.lower()
                    or query_lower in m.category.lower())
            ]
        else:
            self.current_modules = base_modules

        self._update_table()

    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        # Parse unique key: source|id|version
        unique_key = event.row_key.value
        parts = unique_key.split('|')
        if len(parts) != 3:
            return

        source, module_id, version = parts

        # Find the specific module by source, id, and version
        module = None
        for m in self.current_modules:
            if m.source == source and m.id == module_id and m.version == version:
                module = m
                break

        if module:
            # Push screen with callback to handle refresh
            def on_detail_screen_dismiss(refresh_needed):
                if refresh_needed:
                    self._update_table()
                    self.run_worker(self._check_conflicts())

            self.push_screen(
                ModuleDetailScreen(module, self.installer),
                on_detail_screen_dismiss
            )

    async def action_refresh(self) -> None:
        """Refresh the registry."""
        self.notify("Refreshing registry...")
        try:
            await self.registry.fetch()
            self.current_modules = self.registry.get_modules()
            self._update_table()
            await self._check_conflicts()
            self.notify("Registry refreshed")
        except Exception as e:
            self.notify(f"Error refreshing: {e}", severity="error")

    async def action_check_conflicts(self) -> None:
        """Show detailed conflict information."""
        if not self.registry._loaded:
            self.notify("Registry not loaded", severity="error")
            return

        installed_ids = {m.id for m in self.installer.get_installed_modules()}
        installed_modules = [
            m for m in self.registry.get_modules()
            if m.id in installed_ids
        ]

        from bashmod.core.conflicts import ConflictDetector
        conflicts = ConflictDetector.detect_conflicts(installed_modules)
        message = ConflictDetector.format_conflicts(conflicts)
        self.notify(message, timeout=10)

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input").focus()

    def action_filter_category(self) -> None:
        """Show category selection menu."""
        if not self.registry._loaded:
            self.notify("Registry not loaded", severity="error")
            return

        categories = self.registry.get_categories()

        if not categories:
            self.notify("No categories available")
            return

        # Show category selection screen with callback
        def on_category_selected(result):
            # Update filter based on selection
            if result is not None:
                # User selected a category (or "all")
                self.current_category_filter = result

                # Get base modules filtered by category
                if self.current_category_filter:
                    base_modules = [
                        m for m in self.registry.get_modules()
                        if m.category == self.current_category_filter
                    ]
                else:
                    base_modules = self.registry.get_modules()

                # Apply any existing search query
                search_input = self.query_one("#search-input", Input)
                query = search_input.value.strip()
                if query:
                    query_lower = query.lower()
                    self.current_modules = [
                        m for m in base_modules
                        if (query_lower in m.id.lower()
                            or query_lower in m.description.lower()
                            or query_lower in m.category.lower())
                    ]
                else:
                    self.current_modules = base_modules

                # Refresh the table
                self._update_table()

        self.push_screen(
            CategoryFilterScreen(categories, self.current_category_filter),
            on_category_selected
        )

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
Keyboard Shortcuts:

  Navigation:
    ↑/↓        Navigate module list
    Enter      View module details
    Tab        Switch focus

  Search & Filter:
    /          Focus search box
    f          Cycle category filters

  Actions:
    r          Refresh registry from GitHub
    c          Show conflict details
    h          Show this help
    q          Quit application

  Module Details:
    i          Install module
    Esc        Back to list

Category Filtering:
  Press 'f' to cycle through categories.
  Search works within the active category filter.
"""
        self.notify(help_text, timeout=15)
