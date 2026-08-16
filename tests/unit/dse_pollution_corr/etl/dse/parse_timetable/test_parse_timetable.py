from datetime import date

import pytest

from dse_pollution_corr.etl.dse.parse_timetable import (
    _parse_cn_date,
    _parse_en_date,
    _parse_paper,
    _parse_time,
    parse_written_table,
)
from tests.unit.dse_pollution_corr.helpers import raw_document, raw_page, raw_table


@pytest.mark.parametrize(
    ("text", "year", "expected"),
    [
        ("Tuesday, 9 April", 2024, date(2024, 4, 9)),
        ("Thursday, 29th March", 2018, date(2018, 3, 29)),
        ("Tuesday, 9 April", None, None),
    ],
)
def test_parse_en_date(text: str, year: int | None, expected: date | None) -> None:
    assert _parse_en_date(text, year) == expected


def test_parse_cn_date() -> None:
    assert _parse_cn_date("四月九日", 2024) == date(2024, 4, 9)


@pytest.mark.parametrize(
    ("text", "expected_start", "expected_end"),
    [
        ("8:30 - 12:30", "8:30", "12:30"),
        ("# 8:30 - 10:30 *", "8:30", "10:30"),
        ("invalid", None, None),
    ],
)
def test_parse_time(text: str, expected_start: str | None, expected_end: str | None) -> None:
    parsed = _parse_time(text)
    assert parsed["time_start"] == expected_start
    assert parsed["time_end"] == expected_end


@pytest.mark.parametrize(
    ("subject", "name", "paper"),
    [
        ("Visual Arts 1,2", "Visual Arts", "1,2"),
        ("Chinese Language 1", "Chinese Language", "1"),
        ("Biology", "Biology", None),
    ],
)
def test_parse_paper(subject: str, name: str, paper: str | None) -> None:
    assert _parse_paper(subject) == (name, paper)


def test_parse_written_table_visual_arts_row() -> None:
    doc = raw_document(year=2024, path_name="2024_DSE_Timetable.pdf", kind="timetable")
    page = raw_page(page_number=1)
    table = raw_table(
        [
            ["Date", "Time", "Subject / Paper", "科目"],
            [
                "Tuesday, 9 April\n四月九日",
                "8:30 - 12:30",
                "Visual Arts 1,2",
                "視覺藝術",
            ],
        ]
    )
    records = parse_written_table(doc, page, table)
    assert len(records) == 1
    record = records[0]
    assert record["exam_date"] == "2024-04-09"
    assert record["subject_en"] == "Visual Arts"
    assert record["paper"] == "1,2"
    assert record["time_start"] == "8:30"
    assert record["time_end"] == "12:30"
