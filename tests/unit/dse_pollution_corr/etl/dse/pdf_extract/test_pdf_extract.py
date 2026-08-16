from pathlib import Path

import pytest

from dse_pollution_corr.etl.dse.pdf_extract import infer_kind, infer_year, largest_data_table
from tests.unit.dse_pollution_corr.helpers import raw_page, raw_table


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("dseexamstat22_5.pdf", 2022),
        ("2024_DSE_Timetable.pdf", 2024),
        ("unknown.pdf", None),
    ],
)
def test_infer_year(name: str, expected: int | None) -> None:
    assert infer_year(Path(name)) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("data/raw/dse_results/dseexamstat22_5.pdf", "results"),
        ("data/raw/dse_timetable/2024_DSE_Timetable.pdf", "timetable"),
        ("misc/file.pdf", "unknown"),
    ],
)
def test_infer_kind(path: str, expected: str) -> None:
    assert infer_kind(Path(path)) == expected


def test_largest_data_table_skips_title_banners() -> None:
    page = raw_page(
        tables=[
            raw_table([["Title"], ["2022 Results"]], index=0),
            raw_table(
                [
                    ["A", "B", "C", "D"],
                    ["1", "2", "3", "4"],
                    ["5", "6", "7", "8"],
                    ["9", "10", "11", "12"],
                ],
                index=1,
            ),
        ]
    )
    chosen = largest_data_table(page)
    assert chosen is not None
    assert chosen.index == 1


def test_largest_data_table_returns_none_when_only_small_tables() -> None:
    page = raw_page(tables=[raw_table([["A", "B"], ["Title", "Banner"]])])
    assert largest_data_table(page) is None
