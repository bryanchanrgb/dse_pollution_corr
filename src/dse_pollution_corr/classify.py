"""Classify extracted PDF tables into known schemas."""

from __future__ import annotations

from .pdf_extract import RawPage, RawTable
from .text_utils import cell_str

SCHEMA_CATEGORY_A_LEVELS = "category_a_levels"
SCHEMA_CATEGORY_A_CSD = "category_a_csd"
SCHEMA_CATEGORY_B_STANDARD = "category_b_standard"
SCHEMA_CATEGORY_B_CHINESE = "category_b_chinese"
SCHEMA_CATEGORY_C_GRADES = "category_c_grades"
SCHEMA_CATEGORY_C_CEFR = "category_c_cefr"
SCHEMA_CATEGORY_C_TOPIK = "category_c_topik"
SCHEMA_TIMETABLE_WRITTEN = "timetable_written"
SCHEMA_TIMETABLE_PRACTICAL = "timetable_practical"
SCHEMA_TITLE = "title_banner"
SCHEMA_UNKNOWN = "unknown"

RESULTS_SCHEMAS = {
    SCHEMA_CATEGORY_A_LEVELS,
    SCHEMA_CATEGORY_A_CSD,
    SCHEMA_CATEGORY_B_STANDARD,
    SCHEMA_CATEGORY_B_CHINESE,
    SCHEMA_CATEGORY_C_GRADES,
    SCHEMA_CATEGORY_C_CEFR,
    SCHEMA_CATEGORY_C_TOPIK,
}


def _blob(page: RawPage, table: RawTable | None = None) -> str:
    parts = [page.text]
    if table is not None:
        for row in table.rows[:12]:
            parts.append(" ".join(cell_str(c) for c in row))
    return "\n".join(parts)


def table_code(page: RawPage) -> str | None:
    """Return 5, 5a, 5b, ... if this is a results Table 5 page."""
    for line in page.text.splitlines()[:8]:
        match = None
        for token in ("Table", "表"):
            if token in line:
                import re

                found = re.search(rf"(?:Table|表)\s*(5[a-f]?)", line, flags=re.I)
                if found:
                    match = found.group(1).lower()
                    break
        if match:
            return match
    return None


def candidate_type(page: RawPage) -> str | None:
    text = page.text
    if "Day School Candidates" in text or "日校考生" in text:
        return "day_school"
    if "All Candidates" in text or "全體考生" in text:
        return "all"
    return None


def _table_blob(table: RawTable) -> str:
    return "\n".join(cell_str(c) for row in table.rows[:12] for c in row)


def classify_results_table(page: RawPage, table: RawTable) -> str:
    code = table_code(page)
    table_blob = _table_blob(table)
    if table.n_cols <= 2:
        return SCHEMA_TITLE
    if code in {"5e", "5f"}:
        if "TOPIK" in table_blob or "Grade 6" in table_blob or "第6級" in table_blob:
            return SCHEMA_CATEGORY_C_TOPIK
        if "Language proficiency" in table_blob or "語言能力水平" in table_blob:
            return SCHEMA_CATEGORY_C_CEFR
        if "合格" in table_blob or ("Pass" in table_blob and "b+" not in table_blob):
            return SCHEMA_CATEGORY_C_CEFR
        return SCHEMA_CATEGORY_C_GRADES
    if code in {"5c", "5d"}:
        if "Distinction (II)" in table_blob or "表現優異(II)" in table_blob or "優異(II)" in table_blob:
            return SCHEMA_CATEGORY_B_STANDARD
        return SCHEMA_CATEGORY_B_CHINESE
    if code in {"5a", "5b"}:
        if "5**" in table_blob:
            return SCHEMA_CATEGORY_A_LEVELS
        if "Attained" in table_blob or "達標" in table_blob:
            return SCHEMA_CATEGORY_A_CSD
        return SCHEMA_CATEGORY_A_LEVELS
    return SCHEMA_UNKNOWN


def classify_timetable_table(page: RawPage, table: RawTable) -> str:
    blob = _blob(page, table).lower()
    header = " ".join(cell_str(c).lower() for c in (table.rows[0] if table.rows else []))
    if table.n_cols <= 2:
        return SCHEMA_TITLE
    if "practical" in blob or "speaking" in blob or "實習" in blob or "口試" in blob:
        if "visual arts" in header or "subject / paper" in header:
            # Main written table can mention practical in footnotes on the same page.
            if any("practical" in cell_str(c).lower() or "speaking" in cell_str(c).lower() for c in table.rows[0]):
                return SCHEMA_TIMETABLE_PRACTICAL
            # Distinguish by whether the first data rows look like written papers.
            sample = " ".join(cell_str(c) for row in table.rows[1:4] for c in row).lower()
            if "practical" in sample or "speaking" in sample or "實習" in sample or "口試" in sample:
                return SCHEMA_TIMETABLE_PRACTICAL
            return SCHEMA_TIMETABLE_WRITTEN
        return SCHEMA_TIMETABLE_PRACTICAL
    if "subject" in header or "科目" in header:
        return SCHEMA_TIMETABLE_WRITTEN
    return SCHEMA_UNKNOWN


def classify_table(page: RawPage, table: RawTable, kind: str) -> str:
    if kind == "results":
        return classify_results_table(page, table)
    if kind == "timetable":
        return classify_timetable_table(page, table)
    return SCHEMA_UNKNOWN
