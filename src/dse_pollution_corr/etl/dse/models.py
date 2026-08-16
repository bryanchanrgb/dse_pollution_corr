"""Shared datatypes for extracted PDF content."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RawTable:
    index: int
    rows: list[list[Any]]
    n_rows: int
    n_cols: int


@dataclass
class RawPage:
    page_number: int
    width: float
    height: float
    text: str
    tables: list[RawTable] = field(default_factory=list)


@dataclass
class RawDocument:
    path: Path
    year: int | None
    kind: str
    metadata: dict[str, Any]
    pages: list[RawPage] = field(default_factory=list)
