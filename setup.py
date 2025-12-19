#!/usr/bin/env python
"""Setup script for bash-mods."""

from setuptools import setup, find_packages

setup(
    name="bash-mods",
    version="0.1.0",
    description="TUI package manager for modular bash configurations",
    author="David",
    author_email="david@example.com",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "textual>=0.47.0",
        "httpx>=0.25.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bash-mods=bash_mods.__main__:main",
        ],
    },
)
