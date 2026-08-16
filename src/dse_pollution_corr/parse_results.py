"""Schema-specific parsers for HKDSE Table 5 result pages."""

from __future__ import annotations

from typing import Any, Iterator

from .classify import (
    SCHEMA_CATEGORY_A_CSD,
    SCHEMA_CATEGORY_A_LEVELS,
    SCHEMA_CATEGORY_B_CHINESE,
    SCHEMA_CATEGORY_B_STANDARD,
    SCHEMA_CATEGORY_C_CEFR,
    SCHEMA_CATEGORY_C_GRADES,
    SCHEMA_CATEGORY_C_TOPIK,
    candidate_type,
)
from .pdf_extract import RawDocument, RawPage, RawTable
from .text_utils import (
    cell_str,
    detect_gender,
    find_gender_col,
    is_summary_name,
    match_subject_group,
    merge_block_rows,
    parse_int,
    parse_pct,
    split_bilingual,
    split_count_pct,
)

LEVEL_A_GRADES = [
    ("5ss", "5**"),
    ("5s_plus", "5*+"),
    ("5_plus", "5+"),
    ("4_plus", "4+"),
    ("3_plus", "3+"),
    ("2_plus", "2+"),
    ("1_plus", "1+"),
    ("u", "U"),
]

LEVEL_C_GRADES = [
    ("a", "a"),
    ("b_plus", "b+"),
    ("c_plus", "c+"),
    ("d_plus", "d+"),
    ("e_plus", "e+"),
    ("u", "U"),
]

TOPIK_GRADES = [
    ("grade_6", "Grade 6"),
    ("grade_5", "Grade 5"),
    ("grade_4", "Grade 4"),
    ("grade_3", "Grade 3"),
    ("pass_subtotal", "Subtotal"),
]


def _empty_other_c_fields() -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key, _label in LEVEL_C_GRADES + TOPIK_GRADES:
        fields[f"n_{key}"] = None
        fields[f"pct_{key}"] = None
    fields["n_pass"] = None
    fields["pct_pass"] = None
    fields["n_not_pass"] = None
    fields["pct_not_pass"] = None
    return fields


def _scheme_from_level(level: str | None, subject_en: str = "") -> str:
    if level and level.startswith("N"):
        return "jlpt_pass_fail"
    if "Japanese" in (subject_en or ""):
        return "jlpt_pass_fail"
    if level and (level.startswith(("C", "B", "A")) or level == "Subtotal"):
        return "cefr_pass_fail"
    if level and "TOPIK" in level:
        return "topik_grades"
    return "pass_fail"


def _iter_gender_blocks(
    rows: list[list[Any]], gender_col: int
) -> Iterator[tuple[str, list[list[Any]]]]:
    start = None
    for i, row in enumerate(rows):
        if gender_col < len(row) and detect_gender(row[gender_col]) == "male" and "男生" in cell_str(
            row[gender_col]
        ):
            start = i
            break
    if start is None:
        return

    current_gender: str | None = None
    current_rows: list[list[Any]] = []
    pending_prefix: list[list[Any]] = []

    def _has_entered(block: list[list[Any]]) -> bool:
        for item in block:
            if gender_col + 1 < len(item) and parse_int(item[gender_col + 1]) is not None:
                return True
        return False

    def _row_has_entered(row: list[Any]) -> bool:
        return gender_col + 1 < len(row) and parse_int(row[gender_col + 1]) is not None

    for row in rows[start:]:
        gender = detect_gender(row[gender_col] if gender_col < len(row) else "")
        if gender:
            # 女生 and Female are the same block, not two subjects.
            if current_rows and current_gender and gender != current_gender:
                yield current_gender, current_rows
                current_gender = gender
                current_rows = pending_prefix + [row]
                pending_prefix = []
            elif current_rows and current_gender == gender:
                current_rows.append(row)
            else:
                current_gender = gender
                current_rows = pending_prefix + [row]
                pending_prefix = []
        elif current_rows:
            if _has_entered(current_rows) and _row_has_entered(row):
                pending_prefix.append(row)
            else:
                current_rows.append(row)
    if current_rows and current_gender:
        yield current_gender, current_rows + pending_prefix


def _left_labels(merged: list[str], gender_col: int) -> tuple[str, str]:
    left = [cell_str(c) for c in merged[:gender_col]]
    if gender_col <= 1:
        return "", left[0] if left else ""
    while len(left) < 2:
        left.append("")
    return left[0], left[1]


def _looks_rotated_group(text: str) -> bool:
    return any(
        token in text
        for token in (
            "seidutS",
            "scitamehtaM",
            "ecneicS",
            "gniviL",
            "deilppA",
            "ssenisuB",
            "evitaerC",
            "gnireenignE",
            "aideM",
            "secivreS",
            "neseihC",
            "hsilgnE",
            "lanoitacoV",
        )
    )


def _update_names(
    group_cell: str,
    subject_cell: str,
    current_group: tuple[str | None, str | None],
    current_subject: tuple[str, str],
) -> tuple[tuple[str | None, str | None], tuple[str, str]]:
    group = current_group
    subject = current_subject
    if group_cell:
        if _looks_rotated_group(group_cell):
            group = match_subject_group(group_cell)
        else:
            zh, en = split_bilingual(group_cell)
            if en or zh:
                subject = (en, zh)
                group = (None, None)
    if subject_cell:
        zh, en = split_bilingual(subject_cell)
        if en or zh:
            subject = (en, zh)
    return group, subject


def _compose_subject(
    group: tuple[str | None, str | None], subject: tuple[str, str]
) -> tuple[str, str]:
    en, zh = subject
    group_en, _group_zh = group
    if group_en == "Mathematics" and en.startswith(("Compulsory Part", "Extended Part")):
        en = f"Mathematics {en}"
        if zh and not zh.startswith("數學"):
            zh = f"數學{zh}"
    return en, zh


def _numeric_tail(merged: list[str], gender_col: int) -> list[str]:
    return merged[gender_col + 1 :]


def _unpack_counts(
    cells: list[str], n_meta: int, n_grades: int
) -> tuple[list[int | None | float], list[tuple[int | None, float | None]]]:
    meta_cells = cells[:n_meta]
    grade_cells = cells[n_meta : n_meta + n_grades]
    meta: list[int | None | float] = []
    for i, cell in enumerate(meta_cells):
        if i == n_meta - 1 and n_meta >= 3:
            # last meta is usually a percentage (Chinese version %)
            pct = parse_pct(cell)
            meta.append(pct if pct is not None else parse_int(cell))
        else:
            number = parse_int(cell)
            meta.append(number if number is not None else parse_pct(cell))
    grades = [split_count_pct(cell) for cell in grade_cells]
    return meta, grades


def _base_record(
    doc: RawDocument,
    page: RawPage,
    gender: str,
    group: tuple[str | None, str | None],
    subject: tuple[str, str],
) -> dict[str, Any]:
    subject_en, subject_zh = _compose_subject(group, subject)
    return {
        "year": doc.year,
        "candidate_type": candidate_type(page),
        "subject_group_en": group[0],
        "subject_group_zh": group[1],
        "subject_en": subject_en,
        "subject_zh": subject_zh,
        "is_summary": is_summary_name(subject_en, subject_zh),
        "gender": gender,
        "source_file": doc.path.name,
        "source_page": page.page_number,
    }


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


PARSERS = {
    SCHEMA_CATEGORY_A_LEVELS: parse_category_a_levels,
    SCHEMA_CATEGORY_A_CSD: parse_category_a_csd,
    SCHEMA_CATEGORY_B_STANDARD: lambda doc, page, table: parse_category_b(
        doc, page, table, SCHEMA_CATEGORY_B_STANDARD
    ),
    SCHEMA_CATEGORY_B_CHINESE: lambda doc, page, table: parse_category_b(
        doc, page, table, SCHEMA_CATEGORY_B_CHINESE
    ),
    SCHEMA_CATEGORY_C_GRADES: parse_category_c_grades,
    SCHEMA_CATEGORY_C_CEFR: parse_category_c_cefr,
    SCHEMA_CATEGORY_C_TOPIK: parse_category_c_topik,
}


def parse_results_table(
    doc: RawDocument, page: RawPage, table: RawTable, schema: str
) -> list[dict[str, Any]]:
    parser = PARSERS.get(schema)
    if parser is None:
        return []
    return parser(doc, page, table)
