from pathlib import Path

import pandas as pd
import pytest

from dse_pollution_corr.etl.environment.process_environment import (
    _parse_aqhi,
    process_wind_direction,
    read_air_quality_file,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("3", 3.0),
        ("3*", 3.0),
        ("", None),
        ("-", None),
        (None, None),
    ],
)
def test_parse_aqhi(value: object, expected: float | None) -> None:
    assert _parse_aqhi(value) == expected


def test_read_air_quality_file_parses_header_and_long_format(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    lines = [
        "meta,row",
        "meta,row",
        "meta,row",
        "meta,row",
        "meta,row",
        "meta,row",
        "meta,row",
        "Date,Hour,Central,Kwun Tong",
        "2020-05-01,1,3,4",
        "2020-05-01,2,3*,5",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")

    frame = read_air_quality_file(path)
    assert set(frame.columns) == {"date", "hour", "station", "aqhi", "source_file"}
    assert len(frame) == 4
    assert frame.loc[frame["station"] == "Central", "aqhi"].iloc[0] == 3.0
    assert frame.loc[frame["station"] == "Kwun Tong", "aqhi"].iloc[1] == 5.0


def test_process_wind_direction_parses_dates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "wind.csv"
    path.write_text(
        "title\n"
        "title2\n"
        "year,month,day,direction_deg,completeness\n"
        "2024,4,9,90.0,C\n"
        "2024,4,10,180.0,#\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "dse_pollution_corr.etl.environment.process_environment.wind_raw_path",
        lambda: path,
    )

    frame = process_wind_direction()
    assert len(frame) == 2
    assert str(frame.iloc[0]["date"]) == "2024-04-09"
    assert frame.iloc[0]["direction_deg"] == 90.0
    assert frame.iloc[0]["completeness"] == "C"
