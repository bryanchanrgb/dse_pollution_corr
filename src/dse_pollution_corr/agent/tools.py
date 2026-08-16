"""LangChain tools for database access."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from dse_pollution_corr.agent.charts import build_chart
from dse_pollution_corr.db.catalog import list_tables
from dse_pollution_corr.db.schema import describe_table
from dse_pollution_corr.db.guardrails import run_query

_last_query_result: dict[str, Any] | None = None


def get_last_query_result() -> dict[str, Any] | None:
    return _last_query_result


def _format_table(columns: list[str], rows: list[list[Any]], limit: int = 20) -> str:
    preview = rows[:limit]
    payload = {"columns": columns, "rows": preview, "row_count": len(rows)}
    return json.dumps(payload, default=str)


@tool
def list_database_objects() -> str:
    """List tables, views, and query hints for the HKDSE / environment database."""
    return list_tables()


@tool
def describe_database_object(name: str) -> str:
    """Describe columns and documentation for a table or view name."""
    return describe_table(name)


@tool
def run_sql_query(query: str) -> str:
    """Run a read-only SQL SELECT against DuckDB. Always use LIMIT. Prefer analytical views."""
    global _last_query_result
    columns, rows = run_query(query)
    chart = build_chart(columns, rows)
    _last_query_result = {
        "sql": query,
        "columns": columns,
        "rows": rows[:100],
        "row_count": len(rows),
        "chart": chart,
    }
    return _format_table(columns, rows)


AGENT_TOOLS = [list_database_objects, describe_database_object, run_sql_query]
