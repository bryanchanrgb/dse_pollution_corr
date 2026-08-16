"""PDF to raw text/table extraction using pdfplumber."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pdfplumber


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


def infer_year(path: Path) -> int | None:
    name = path.name
    match = re.search(r"(20\d{2})", name)
    if match:
        return int(match.group(1))
    match = re.search(r"dseexamstat(\d{2})", name)
    if match:
        return 2000 + int(match.group(1))
    return None


def infer_kind(path: Path) -> str:
    lowered = str(path).lower()
    if "timetable" in lowered:
        return "timetable"
    if "dseexamstat" in lowered or "dse_results" in lowered:
        return "results"
    return "unknown"


def extract_pdf(path: Path | str) -> RawDocument:
    """Extract page text and tables from a PDF."""
    path = Path(path)
    pages: list[RawPage] = []
    with pdfplumber.open(path) as pdf:
        metadata = dict(pdf.metadata or {})
        for i, page in enumerate(pdf.pages):
            raw_tables = page.extract_tables() or []
            tables = [
                RawTable(
                    index=ti,
                    rows=table,
                    n_rows=len(table),
                    n_cols=len(table[0]) if table else 0,
                )
                for ti, table in enumerate(raw_tables)
            ]
            pages.append(
                RawPage(
                    page_number=i + 1,
                    width=float(page.width or 0),
                    height=float(page.height or 0),
                    text=page.extract_text() or "",
                    tables=tables,
                )
            )
    return RawDocument(
        path=path,
        year=infer_year(path),
        kind=infer_kind(path),
        metadata=metadata,
        pages=pages,
    )


def largest_data_table(page: RawPage) -> RawTable | None:
    """Return the largest table on a page, skipping title-only 2-column banners."""
    candidates = [t for t in page.tables if t.n_cols >= 3 and t.n_rows >= 4]
    if not candidates:
        return None
    return max(candidates, key=lambda t: t.n_rows * t.n_cols)
