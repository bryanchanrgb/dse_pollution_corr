import pytest

from dse_pollution_corr.etl.dse.text_utils import (
    chinese_numeral,
    detect_gender,
    parse_int,
    parse_pct,
    split_bilingual,
    split_count_pct,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1,234", 1234),
        ("5201\n3.1%", 5201),
        ("-", None),
        ("", None),
    ],
)
def test_parse_int(value: str, expected: int | None) -> None:
    assert parse_int(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("3.1%", 3.1),
        ("92.7", 92.7),
        ("-", None),
    ],
)
def test_parse_pct(value: str, expected: float | None) -> None:
    assert parse_pct(value) == expected


def test_split_count_pct_stacked_cell() -> None:
    count, pct = split_count_pct("156\n3.1%")
    assert count == 156
    assert pct == 3.1


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("男生 Male", "male"),
        ("女生 Female", "female"),
        ("總數 Total", "total"),
        ("Biology", None),
    ],
)
def test_detect_gender(value: str, expected: str | None) -> None:
    assert detect_gender(value) == expected


def test_split_bilingual() -> None:
    zh, en = split_bilingual("生物\nBiology")
    assert zh == "生物"
    assert en == "Biology"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("十", 10),
        ("十五", 15),
        ("二十", 20),
        ("3", 3),
    ],
)
def test_chinese_numeral(text: str, expected: int) -> None:
    assert chinese_numeral(text) == expected
