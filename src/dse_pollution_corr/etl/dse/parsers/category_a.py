"""Category A level (5**-U) result parser."""

from __future__ import annotations

from typing import Any

from dse_pollution_corr.etl.dse.models import RawDocument, RawPage, RawTable
from dse_pollution_corr.etl.dse.parsers._shared import (
    LEVEL_A_GRADES,
    _base_record,
    _iter_gender_blocks,
    _left_labels,
    _numeric_tail,
    _unpack_counts,
    _update_names,
)
from dse_pollution_corr.etl.dse.text_utils import find_gender_col, merge_block_rows

def parse_category_a_levels(
    doc: RawDocument, page: RawPage, table: RawTable
) -> list[dict[str, Any]]:
    gender_col = find_gender_col(table.rows)
    if gender_col is None:
        return []
    records: list[dict[str, Any]] = []
    group: tuple[str | None, str | None] = (None, None)
    subject = ("", "")
    for gender, block in _iter_gender_blocks(table.rows, gender_col):
        merged = merge_block_rows(block)
        group_cell, subject_cell = _left_labels(merged, gender_col)
        group, subject = _update_names(group_cell, subject_cell, group, subject)
        if not subject[0] and not subject[1]:
            continue
        meta, grades = _unpack_counts(_numeric_tail(merged, gender_col), n_meta=3, n_grades=8)
        rec = _base_record(doc, page, gender, group, subject)
        rec.update(
            {
                "n_entered": meta[0] if len(meta) > 0 else None,
                "n_sat": meta[1] if len(meta) > 1 else None,
                "chinese_version_pct": meta[2] if len(meta) > 2 else None,
            }
        )
        for (key, _label), (count, pct) in zip(LEVEL_A_GRADES, grades + [(None, None)] * 8):
            rec[f"n_{key}"] = count
            rec[f"pct_{key}"] = pct
        records.append(rec)
    return records


