"""DuckDB connection and SQL guardrails."""

from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Any, Iterator

import duckdb

from dse_pollution_corr.paths import db_path

FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|COPY|EXPORT|IMPORT|"
    r"LOAD|INSTALL|PRAGMA|SET|CALL|EXECUTE)\b",
    re.I,
)
DEFAULT_ROW_LIMIT = 500


def validate_sql(sql: str) -> str:
    text = sql.strip().rstrip(";")
    if not text:
        raise ValueError("Empty SQL")
    if ";" in text:
        raise ValueError("Only a single SELECT statement is allowed")
    if not re.match(r"(?is)^\s*(WITH\b|SELECT\b)", text):
        raise ValueError("Only SELECT queries are allowed")
    if FORBIDDEN.search(text):
        raise ValueError("Query contains forbidden keywords")
    if not re.search(r"(?is)\bLIMIT\b", text):
        text = f"{text}\nLIMIT {DEFAULT_ROW_LIMIT}"
    return text


@contextmanager
def readonly_connection(path: str | None = None) -> Iterator[duckdb.DuckDBPyConnection]:
    conn = duckdb.connect(str(path or db_path()), read_only=True)
    try:
        yield conn
    finally:
        conn.close()


def run_query(sql: str, path: str | None = None) -> tuple[list[str], list[list[Any]]]:
    safe_sql = validate_sql(sql)
    with readonly_connection(path) as conn:
        result = conn.execute(safe_sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
    return columns, rows
