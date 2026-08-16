"""Category A CSD result parser."""

from __future__ import annotations

from typing import Any

from dse_pollution_corr.etl.dse.models import RawDocument, RawPage, RawTable
from dse_pollution_corr.etl.dse.parsers._shared import (
    _base_record,
    _iter_gender_blocks,
    _left_labels,
    _numeric_tail,
    _unpack_counts,
    _update_names,
    cell_str,
    find_gender_col,
    merge_block_rows,
    split_bilingual,
)

def _csd_record(
    doc: RawDocument,
    page: RawPage,
    gender: str,
    group: tuple[str | None, str | None],
    subject: tuple[str, str],
    merged: list[str],
    gender_col: int,
) -> dict[str, Any]:
    meta, grades = _unpack_counts(_numeric_tail(merged, gender_col), n_meta=3, n_grades=2)
    rec = _base_record(doc, page, gender, group, subject)
    rec.update(
        {
            "n_entered": meta[0] if len(meta) > 0 else None,
            "n_sat": meta[1] if len(meta) > 1 else None,
            "chinese_version_pct": meta[2] if len(meta) > 2 else None,
            "n_attained": grades[0][0] if grades else None,
            "pct_attained": grades[0][1] if grades else None,
            "n_unattained": grades[1][0] if len(grades) > 1 else None,
            "pct_unattained": grades[1][1] if len(grades) > 1 else None,
        }
    )
    return rec


def _parse_smashed_csd(
    doc: RawDocument,
    page: RawPage,
    table: RawTable,
    gender_col: int,
) -> list[dict[str, Any]]:
    """All-candidates CSD tables sometimes collapse Male/Female/Total into one cell."""
    start = None
    for i, row in enumerate(table.rows):
        cell = cell_str(row[gender_col] if gender_col < len(row) else "")
        if "男生" in cell and "女生" in cell:
            start = i
            break
    if start is None:
        return []
    subject = ("", "")
    first = table.rows[start]
    left = [cell_str(c) for c in first[:gender_col] if cell_str(c)]
    if left:
        zh, en = split_bilingual(left[0])
        subject = (en, zh)
    data_rows = table.rows[start:]
    # Typical layout: male combined; female counts; female pcts; total combined.
    blocks = {
        "male": [data_rows[0]] if data_rows else [],
        "female": data_rows[1:3] if len(data_rows) >= 3 else data_rows[1:2],
        "total": [data_rows[3]] if len(data_rows) >= 4 else [],
    }
    records = []
    for gender, rows in blocks.items():
        if not rows:
            continue
        merged = merge_block_rows(rows)
        records.append(_csd_record(doc, page, gender, (None, None), subject, merged, gender_col))
    return records


def parse_category_a_csd(
    doc: RawDocument, page: RawPage, table: RawTable
) -> list[dict[str, Any]]:
    gender_col = find_gender_col(table.rows)
    if gender_col is None:
        return []
    for row in table.rows:
        cell = cell_str(row[gender_col] if gender_col < len(row) else "")
        if "男生" in cell and "女生" in cell:
            return _parse_smashed_csd(doc, page, table, gender_col)
    records: list[dict[str, Any]] = []
    group: tuple[str | None, str | None] = (None, None)
    subject = ("", "")
    for gender, block in _iter_gender_blocks(table.rows, gender_col):
        merged = merge_block_rows(block)
        group_cell, subject_cell = _left_labels(merged, gender_col)
        group, subject = _update_names(group_cell, subject_cell, group, subject)
        if not subject[0] and not subject[1]:
            continue
        records.append(_csd_record(doc, page, gender, group, subject, merged, gender_col))
    return records


