"""Static YAML catalog metadata for the agent."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml

from dse_pollution_corr.paths import catalog_path


@lru_cache
def load_catalog() -> dict[str, Any]:
    with catalog_path().open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def list_tables() -> str:
    catalog = load_catalog()
    lines = ["Tables:"]
    for name, meta in catalog.get("tables", {}).items():
        lines.append(f"- {name}: {meta.get('description', '')}")
    lines.append("\nViews:")
    for name, meta in catalog.get("views", {}).items():
        lines.append(f"- {name}: {meta.get('description', '')}")
    lines.append("\nQuery hints:")
    for hint in catalog.get("query_hints", []):
        lines.append(f"- {hint}")
    return "\n".join(lines)
