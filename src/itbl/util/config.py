"""Configuration loading and management."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    # Check for config in project root, then fall back to package config
    project_root = Path(__file__).parent.parent.parent.parent
    config_dir = project_root / "config"
    if config_dir.exists():
        return config_dir
    # Package default
    return Path(__file__).parent.parent.parent / "config"


def load_yaml(config_name: str, config_dir: Path | None = None) -> Dict[str, Any]:
    """Load a YAML config file."""
    if config_dir is None:
        config_dir = get_config_dir()
    config_path = config_dir / config_name
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sheets_config(config_dir: Path | None = None) -> Dict[str, Any]:
    """Load sheets.yaml configuration."""
    return load_yaml("sheets.yaml", config_dir)


def load_rules_config(config_dir: Path | None = None) -> Dict[str, Any]:
    """Load rules.yaml configuration."""
    return load_yaml("rules.yaml", config_dir)


def load_vendors_config(config_dir: Path | None = None) -> Dict[str, Any]:
    """Load vendors.yaml configuration."""
    return load_yaml("vendors.yaml", config_dir)

