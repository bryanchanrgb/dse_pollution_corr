"""Shared helpers for Table 5 result parsers."""

from __future__ import annotations

from typing import Any, Iterator

from dse_pollution_corr.etl.dse.classify import candidate_type
from dse_pollution_corr.etl.dse.models import RawDocument, RawPage, RawTable
from dse_pollution_corr.etl.dse.text_utils import (
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


