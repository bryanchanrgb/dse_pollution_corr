from pathlib import Path

import pytest

from dse_pollution_corr.etl.dse.classify import (
    SCHEMA_CATEGORY_A_CSD,
    SCHEMA_CATEGORY_A_LEVELS,
    SCHEMA_CATEGORY_B_STANDARD,
    SCHEMA_CATEGORY_C_CEFR,
    SCHEMA_CATEGORY_C_GRADES,
    SCHEMA_TIMETABLE_PRACTICAL,
    SCHEMA_TIMETABLE_WRITTEN,
    candidate_type,
    classify_table,
    table_code,
)
from tests.unit.dse_pollution_corr.helpers import raw_page, raw_table


def test_table_code_reads_results_table_label() -> None:
    page = raw_page("HKDSE\nTable 5a\nDay School Candidates")
    assert table_code(page) == "5a"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Day School Candidates 日校考生", "day_school"),
        ("All Candidates 全體考生", "all"),
        ("Some other page", None),
    ],
)
def test_candidate_type(text: str, expected: str | None) -> None:
    assert candidate_type(raw_page(text)) == expected


def test_classify_category_a_levels_table() -> None:
    page = raw_page("Table 5a\nDay School Candidates")
    table = raw_table(
        [
            ["Subject", "Gender", "Entered", "5**", "5*+"],
            ["Biology", "男生 Male", "5201", "156\n3.1%", "200\n4.0%"],
            ["", "", "", "5+", "4+"],
        ]
    )
    assert classify_table(page, table, "results") == SCHEMA_CATEGORY_A_LEVELS


def test_classify_category_a_csd_table() -> None:
    page = raw_page("Table 5b\nAll Candidates")
    table = raw_table(
        [
            ["Subject", "Gender", "Attained", "Unattained"],
            ["CSD", "男生 Male", "100\n90.0%", "10\n10.0%"],
        ]
    )
    assert classify_table(page, table, "results") == SCHEMA_CATEGORY_A_CSD


def test_classify_category_b_standard_table() -> None:
    page = raw_page("Table 5c")
    table = raw_table(
        [
            ["Subject", "Gender", "Distinction (II)"],
            ["Animal Care", "total", "10\n18.5%"],
        ]
    )
    assert classify_table(page, table, "results") == SCHEMA_CATEGORY_B_STANDARD


def test_classify_category_c_tables() -> None:
    grades_page = raw_page("Table 5e")
    grades_table = raw_table([["Subject", "a", "b+"], ["French", "4\n22.2%", "1\n5.0%"]])
    assert classify_table(grades_page, grades_table, "results") == SCHEMA_CATEGORY_C_GRADES

    cefr_page = raw_page("Table 5f")
    cefr_table = raw_table(
        [["Subject", "Language proficiency", "Pass"], ["Japanese", "N1", "54\n94.7%"]]
    )
    assert classify_table(cefr_page, cefr_table, "results") == SCHEMA_CATEGORY_C_CEFR


def test_classify_timetable_written_vs_practical() -> None:
    written_page = raw_page("2024 EXAMINATION TIMETABLE")
    written_table = raw_table(
        [
            ["Date", "Time", "Subject / Paper", "科目"],
            ["9 April", "8:30-12:30", "Visual Arts 1,2", "視覺藝術"],
        ]
    )
    assert classify_table(written_page, written_table, "timetable") == SCHEMA_TIMETABLE_WRITTEN

    practical_page = raw_page("Practical and speaking examinations")
    practical_table = raw_table(
        [
            ["Date", "Time", "Subject / Paper", "Subject"],
            ["April", "9:00-12:00", "English Speaking", "英語口試"],
        ]
    )
    assert classify_table(practical_page, practical_table, "timetable") == SCHEMA_TIMETABLE_PRACTICAL
