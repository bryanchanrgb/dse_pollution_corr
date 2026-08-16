"""Category C (Other Languages) result parsers."""

from __future__ import annotations

from typing import Any

from dse_pollution_corr.etl.dse.models import RawDocument, RawPage, RawTable
from dse_pollution_corr.etl.dse.parsers._shared import (
    LEVEL_C_GRADES,
    TOPIK_GRADES,
    _base_record,
    _empty_other_c_fields,
    _iter_gender_blocks,
    _left_labels,
    _numeric_tail,
    _scheme_from_level,
    _unpack_counts,
    _update_names,
    cell_str,
    find_gender_col,
    merge_block_rows,
    split_bilingual,
)

def parse_category_c_grades(
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
        meta, grades = _unpack_counts(_numeric_tail(merged, gender_col), n_meta=2, n_grades=6)
        rec = _base_record(doc, page, gender, group, subject)
        rec.update(_empty_other_c_fields())
        rec.update(
            {
                "language_proficiency_level": None,
                "n_entered": meta[0] if len(meta) > 0 else None,
                "n_sat": meta[1] if len(meta) > 1 else None,
                "grading_scheme": "cambridge_grades",
            }
        )
        for (key, _label), (count, pct) in zip(LEVEL_C_GRADES, grades + [(None, None)] * 6):
            rec[f"n_{key}"] = count
            rec[f"pct_{key}"] = pct
        records.append(rec)
    return records


def parse_category_c_cefr(
    doc: RawDocument, page: RawPage, table: RawTable
) -> list[dict[str, Any]]:
    gender_col = find_gender_col(table.rows)
    if gender_col is None:
        return []
    records: list[dict[str, Any]] = []
    subject = ("", "")
    level = ""
    for gender, block in _iter_gender_blocks(table.rows, gender_col):
        merged = merge_block_rows(block)
        left = [cell_str(c) for c in merged[:gender_col] if cell_str(c)]
        if left:
            # subject in col 0, proficiency in the last left col
            if len(left) == 1:
                # either a new subject or a new level
                cell = left[0]
                if any(tok in cell for tok in ("Language", "語", "所有", "All ")):
                    zh, en = split_bilingual(cell)
                    subject = (en, zh)
                else:
                    level = cell.replace("\n", " ").strip()
                    if "小計" in cell or "Subtotal" in cell:
                        level = "Subtotal"
            else:
                zh, en = split_bilingual(left[0])
                if en or zh:
                    subject = (en, zh)
                level_cell = left[-1]
                if "小計" in level_cell or "Subtotal" in level_cell:
                    level = "Subtotal"
                else:
                    level = level_cell.replace("\n", " ").strip()
        if not subject[0] and not subject[1]:
            continue
        meta, grades = _unpack_counts(_numeric_tail(merged, gender_col), n_meta=2, n_grades=2)
        rec = _base_record(doc, page, gender, (None, None), subject)
        rec.update(_empty_other_c_fields())
        rec.update(
            {
                "language_proficiency_level": level or None,
                "n_entered": meta[0] if len(meta) > 0 else None,
                "n_sat": meta[1] if len(meta) > 1 else None,
                "grading_scheme": _scheme_from_level(level or None, subject[0]),
                "n_pass": grades[0][0] if grades else None,
                "pct_pass": grades[0][1] if grades else None,
                "n_not_pass": grades[1][0] if len(grades) > 1 else None,
                "pct_not_pass": grades[1][1] if len(grades) > 1 else None,
            }
        )
        records.append(rec)
    return records


def parse_category_c_topik(
    doc: RawDocument, page: RawPage, table: RawTable
) -> list[dict[str, Any]]:
    gender_col = find_gender_col(table.rows)
    if gender_col is None:
        return []
    records: list[dict[str, Any]] = []
    subject = ("", "")
    level = "TOPIK II"
    for gender, block in _iter_gender_blocks(table.rows, gender_col):
        merged = merge_block_rows(block)
        left = [cell_str(c) for c in merged[:gender_col] if cell_str(c)]
        if left:
            first = left[0]
            if "Language" in first or "語" in first:
                zh, en = split_bilingual(first)
                subject = (en, zh)
            if any("TOPIK" in cell for cell in left):
                level = next(cell.replace("\n", " ").strip() for cell in left if "TOPIK" in cell)
        if not subject[0] and not subject[1]:
            continue
        meta, grades = _unpack_counts(_numeric_tail(merged, gender_col), n_meta=2, n_grades=6)
        rec = _base_record(doc, page, gender, (None, None), subject)
        rec.update(_empty_other_c_fields())
        rec.update(
            {
                "language_proficiency_level": level,
                "n_entered": meta[0] if len(meta) > 0 else None,
                "n_sat": meta[1] if len(meta) > 1 else None,
                "grading_scheme": "topik_grades",
                "n_pass": grades[4][0] if len(grades) > 4 else None,
                "pct_pass": grades[4][1] if len(grades) > 4 else None,
                "n_not_pass": grades[5][0] if len(grades) > 5 else None,
                "pct_not_pass": grades[5][1] if len(grades) > 5 else None,
            }
        )
        for (key, _label), (count, pct) in zip(TOPIK_GRADES, grades[:5] + [(None, None)] * 5):
            rec[f"n_{key}"] = count
            rec[f"pct_{key}"] = pct
        records.append(rec)
    return records

