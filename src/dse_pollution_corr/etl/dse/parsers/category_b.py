"""Category B (Applied Learning) result parser."""

from __future__ import annotations

from typing import Any

from dse_pollution_corr.etl.dse.classify import SCHEMA_CATEGORY_B_CHINESE, SCHEMA_CATEGORY_B_STANDARD
from dse_pollution_corr.etl.dse.models import RawDocument, RawPage, RawTable
from dse_pollution_corr.etl.dse.parsers._shared import (
    _base_record,
    _iter_gender_blocks,
    _left_labels,
    _numeric_tail,
    _unpack_counts,
    _update_names,
    find_gender_col,
    merge_block_rows,
)

def parse_category_b(
    doc: RawDocument, page: RawPage, table: RawTable, scheme: str
) -> list[dict[str, Any]]:
    gender_col = find_gender_col(table.rows)
    if gender_col is None:
        return []
    n_grades = 4 if scheme == SCHEMA_CATEGORY_B_STANDARD else 3
    records: list[dict[str, Any]] = []
    group: tuple[str | None, str | None] = (None, None)
    subject = ("", "")
    for gender, block in _iter_gender_blocks(table.rows, gender_col):
        merged = merge_block_rows(block)
        group_cell, subject_cell = _left_labels(merged, gender_col)
        group, subject = _update_names(group_cell, subject_cell, group, subject)
        if not subject[0] and not subject[1]:
            continue
        meta, grades = _unpack_counts(_numeric_tail(merged, gender_col), n_meta=2, n_grades=n_grades)
        rec = _base_record(doc, page, gender, group, subject)
        rec["grading_scheme"] = (
            "apl_standard" if scheme == SCHEMA_CATEGORY_B_STANDARD else "apl_chinese"
        )
        rec["n_entered"] = meta[0] if len(meta) > 0 else None
        rec["n_fulfilled_attendance"] = meta[1] if len(meta) > 1 else None
        if scheme == SCHEMA_CATEGORY_B_STANDARD:
            rec.update(
                {
                    "n_distinction_ii": grades[0][0] if grades else None,
                    "pct_distinction_ii": grades[0][1] if grades else None,
                    "n_distinction_i_or_above": grades[1][0] if len(grades) > 1 else None,
                    "pct_distinction_i_or_above": grades[1][1] if len(grades) > 1 else None,
                    "n_attained_or_above": grades[2][0] if len(grades) > 2 else None,
                    "pct_attained_or_above": grades[2][1] if len(grades) > 2 else None,
                    "n_unattained": grades[3][0] if len(grades) > 3 else None,
                    "pct_unattained": grades[3][1] if len(grades) > 3 else None,
                    "n_distinction": None,
                    "pct_distinction": None,
                }
            )
        else:
            rec.update(
                {
                    "n_distinction_ii": None,
                    "pct_distinction_ii": None,
                    "n_distinction_i_or_above": None,
                    "pct_distinction_i_or_above": None,
                    "n_distinction": grades[0][0] if grades else None,
                    "pct_distinction": grades[0][1] if grades else None,
                    "n_attained_or_above": grades[1][0] if len(grades) > 1 else None,
                    "pct_attained_or_above": grades[1][1] if len(grades) > 1 else None,
                    "n_unattained": grades[2][0] if len(grades) > 2 else None,
                    "pct_unattained": grades[2][1] if len(grades) > 2 else None,
                }
            )
        records.append(rec)
    return records


