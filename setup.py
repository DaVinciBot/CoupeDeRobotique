"""Setup script for robot log manager."""

from setuptools import find_packages, setup

setup(
    name="robot-log-manager",
    version="1.0.0",
    description="Log manager for robot logs with filtering and indexing",
    author="DaVinciBot Team",
    packages=find_packages(where="common"),
    package_dir={"": "common"},
    entry_points={
        "console_scripts": [
            "lgppp_manager=log_manager.cli:main",
        ],
    },
    install_requires=[
        # Pas de dépendances externes, tout est en stdlib
    ],
    python_requires=">=3.13",
)
