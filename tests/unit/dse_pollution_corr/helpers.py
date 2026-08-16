"""Test helpers mirroring production dataclasses."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from dse_pollution_corr.etl.dse.models import RawDocument, RawPage, RawTable


def raw_table(rows: list[list[Any]], *, index: int = 0) -> RawTable:
    return RawTable(
        index=index,
        rows=rows,
        n_rows=len(rows),
        n_cols=max((len(row) for row in rows), default=0),
    )


def raw_page(
    text: str = "",
    *,
    tables: list[RawTable] | None = None,
    page_number: int = 1,
) -> RawPage:
    return RawPage(
        page_number=page_number,
        width=595.0,
        height=842.0,
        text=text,
        tables=tables or [],
    )


def raw_document(
    *,
    year: int | None = 2022,
    kind: str = "results",
    path_name: str = "dseexamstat22_5.pdf",
    pages: list[RawPage] | None = None,
) -> RawDocument:
    return RawDocument(
        path=Path(path_name),
        year=year,
        kind=kind,
        metadata={},
        pages=pages or [raw_page()],
    )


def write_csv(path: Path, header: list[str], rows: list[list[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
