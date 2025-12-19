"""Main entry point for bash-mods CLI."""

import sys
import argparse
from bash_mods.tui import BashModsApp


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TUI package manager for modular bash configurations"
    )
    parser.add_argument(
        "--registry-url",
        help="Custom registry URL (default: GitHub)",
        default=None
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode (enables Textual devtools)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="bash-mods 0.1.0"
    )

    args = parser.parse_args()

    # Run the TUI app
    app = BashModsApp(registry_url=args.registry_url)
    if args.dev:
        # Run with dev mode - shows all errors and enables devtools
        import os
        os.environ["TEXTUAL"] = "devtools"
        app.run()
    else:
        app.run()


if __name__ == "__main__":
    main()
