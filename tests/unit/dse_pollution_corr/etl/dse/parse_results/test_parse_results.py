import pytest

from dse_pollution_corr.etl.dse.parse_results import (
    _compose_subject,
    _scheme_from_level,
    parse_category_a_levels,
)
from tests.unit.dse_pollution_corr.helpers import raw_document, raw_page, raw_table


def test_compose_subject_prefixes_mathematics_parts() -> None:
    subject = _compose_subject(
        ("Mathematics", "數學"),
        ("Compulsory Part", "必修部分"),
    )
    assert subject == ("Mathematics Compulsory Part", "數學必修部分")


@pytest.mark.parametrize(
    ("level", "subject_en", "expected"),
    [
        ("N1", "Japanese Language", "jlpt_pass_fail"),
        ("C1", "French Language", "cefr_pass_fail"),
        ("TOPIK Grade 6", "Korean Language", "topik_grades"),
        (None, "French Language", "pass_fail"),
    ],
)
def test_scheme_from_level(level: str | None, subject_en: str, expected: str) -> None:
    assert _scheme_from_level(level, subject_en) == expected


def test_parse_category_a_levels_extracts_biology_male_counts() -> None:
    doc = raw_document(year=2022)
    page = raw_page("Table 5a\nDay School Candidates 日校考生")
    table = raw_table(
        [
            ["Group", "Subject", "Gender", "Entered", "Sat", "Chi%", "5**", "5*+", "5+", "4+", "3+", "2+", "1+", "U"],
            ["", "Biology\n生物", "男生\nMale", "5201", "5000", "10.0", "156\n3.1%", "200\n4.0%", "500\n10.0%", "1000\n20.0%", "1500\n30.0%", "2000\n40.0%", "2500\n50.0%", "100\n2.0%"],
            ["", "", "女生\nFemale", "6662", "6500", "12.0", "100\n1.5%", "150\n2.3%", "400\n6.2%", "900\n13.8%", "1400\n21.5%", "1900\n29.2%", "2400\n36.9%", "120\n1.8%"],
        ]
    )
    records = parse_category_a_levels(doc, page, table)
    male = next(record for record in records if record["gender"] == "male")
    assert male["subject_en"] == "Biology"
    assert male["candidate_type"] == "day_school"
    assert male["n_entered"] == 5201
    assert male["n_5ss"] == 156
    assert male["pct_5ss"] == 3.1
