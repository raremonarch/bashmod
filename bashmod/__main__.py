"""Main entry point for bashmod CLI."""

import sys
import argparse
import logging
from pathlib import Path
from bashmod.tui import BashMod


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TUI package manager for modular bash configurations"
    )
    parser.add_argument(
        "--registry-url",
        action="append",
        dest="registry_urls",
        help="Registry URL (can be specified multiple times)",
        default=None
    )
    parser.add_argument(
        "--registry-path",
        action="append",
        dest="registry_paths",
        help="Local registry path (can be specified multiple times)",
        default=None
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help=(
            "Run in development mode "
            "(logs errors to stderr and enables Textual devtools)"
        )
    )
    parser.add_argument(
        "--version",
        action="version",
        version="bashmod 0.1.0"
    )

    args = parser.parse_args()

    # Run the TUI app
    app = BashMod(
        registry_urls=args.registry_urls,
        registry_paths=args.registry_paths
    )
    if args.dev:
        # Run with dev mode - logs errors to stderr
        import os
        import traceback
        os.environ["TEXTUAL"] = "devtools"

        # Configure logging to stderr
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            stream=sys.stderr
        )

        # Also log to file for persistence
        log_file = Path.home() / '.cache' / 'bashmod' / 'debug.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)

        print(f"Dev mode: Logging to stderr and {log_file}", file=sys.stderr)

        try:
            app.run()
        except Exception as e:
            # Log the full traceback
            error_msg = f"\n{'='*60}\nFATAL ERROR:\n{traceback.format_exc()}{'='*60}\n"
            print(error_msg, file=sys.stderr)
            logging.error(f"Application crashed: {e}", exc_info=True)
            sys.exit(1)
    else:
        app.run()


if __name__ == "__main__":
    main()
