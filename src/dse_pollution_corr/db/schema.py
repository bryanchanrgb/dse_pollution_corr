"""Live DuckDB schema introspection."""

from __future__ import annotations

from dse_pollution_corr.db.catalog import load_catalog
from dse_pollution_corr.db.guardrails import run_query
from dse_pollution_corr.paths import project_root


def describe_table(name: str) -> str:
    catalog = load_catalog()
    meta = catalog.get("tables", {}).get(name) or catalog.get("views", {}).get(name)
    if meta is None:
        return f"Unknown table or view: {name}"

    columns, rows = run_query(
        f"SELECT column_name, data_type FROM information_schema.columns "
        f"WHERE table_name = '{name}' ORDER BY ordinal_position LIMIT 100"
    )
    col_lines = [f"  {row[0]} ({row[1]})" for row in rows[:40]]

    readme = meta.get("readme")
    readme_text = ""
    if readme:
        readme_file = project_root() / readme
        if readme_file.exists():
            readme_text = readme_file.read_text(encoding="utf-8")[:2000]

    parts = [
        f"{name}: {meta.get('description', '')}",
        "Columns:",
        *col_lines,
    ]
    if readme_text:
        parts.extend(["", "README excerpt:", readme_text])
    return "\n".join(parts)
