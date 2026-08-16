"""Integration test fixtures (temp DuckDB, processed CSV tree)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit.dse_pollution_corr.helpers import write_csv


@pytest.fixture
def minimal_processed_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Minimal processed CSV tree for DuckDB integration tests."""
    dse_results = tmp_path / "dse_results"
    dse_timetable = tmp_path / "dse_timetable"
    environment = tmp_path / "environment"

    write_csv(
        dse_results / "category_a_subject_results.csv",
        [
            "year",
            "candidate_type",
            "subject_group_en",
            "subject_group_zh",
            "subject_en",
            "subject_zh",
            "is_summary",
            "gender",
            "source_file",
            "source_page",
            "n_entered",
            "n_sat",
            "chinese_version_pct",
            "n_5ss",
            "pct_5ss",
            "n_5s_plus",
            "pct_5s_plus",
            "n_5_plus",
            "pct_5_plus",
            "n_4_plus",
            "pct_4_plus",
            "n_3_plus",
            "pct_3_plus",
            "n_2_plus",
            "pct_2_plus",
            "n_1_plus",
            "pct_1_plus",
            "n_u",
            "pct_u",
        ],
        [
            [
                2022,
                "day_school",
                "",
                "",
                "Biology",
                "生物",
                "False",
                "male",
                "dseexamstat22_5.pdf",
                1,
                5201,
                5000,
                10.0,
                156,
                3.1,
                200,
                4.0,
                500,
                10.0,
                1000,
                20.0,
                1500,
                30.0,
                2000,
                40.0,
                2500,
                50.0,
                100,
                2.0,
            ],
        ],
    )
    write_csv(
        dse_results / "category_a_csd_results.csv",
        [
            "year",
            "candidate_type",
            "subject_group_en",
            "subject_group_zh",
            "subject_en",
            "subject_zh",
            "is_summary",
            "gender",
            "source_file",
            "source_page",
            "n_entered",
            "n_sat",
            "chinese_version_pct",
            "n_attained",
            "pct_attained",
            "n_unattained",
            "pct_unattained",
        ],
        [[2024, "day_school", "", "", "CSD", "公民", "False", "male", "x.pdf", 1, 1, 1, 1, 1, 1, 0, 0]],
    )
    write_csv(
        dse_results / "category_b_subject_results.csv",
        [
            "year",
            "candidate_type",
            "subject_group_en",
            "subject_group_zh",
            "subject_en",
            "subject_zh",
            "is_summary",
            "gender",
            "grading_scheme",
            "source_file",
            "source_page",
            "n_entered",
            "n_fulfilled_attendance",
        ],
        [[2022, "day_school", "", "", "Animal Care", "動物護理", "False", "total", "apl_standard", "x.pdf", 1, 1, 1]],
    )
    write_csv(
        dse_results / "category_c_subject_results.csv",
        [
            "year",
            "candidate_type",
            "subject_group_en",
            "subject_group_zh",
            "subject_en",
            "subject_zh",
            "is_summary",
            "gender",
            "grading_scheme",
            "language_proficiency_level",
            "source_file",
            "source_page",
            "n_entered",
            "n_pass",
            "pct_pass",
        ],
        [[2022, "day_school", "", "", "French Language", "法語", "False", "male", "cambridge_grades", "", "x.pdf", 1, 1, 1, 1]],
    )
    write_csv(
        dse_timetable / "written_papers.csv",
        [
            "year",
            "exam_date",
            "date_text_en",
            "date_text_zh",
            "subject_en",
            "subject_zh",
            "paper",
            "is_reserve",
            "source_file",
            "source_page",
            "time_raw",
            "time_start",
            "time_end",
            "has_listening_reporting_mark",
            "has_approx_end_mark",
        ],
        [
            [
                2024,
                "2024-04-09",
                "Tuesday, 9 April",
                "四月九日",
                "Visual Arts",
                "視覺藝術",
                "1,2",
                "False",
                "2024_DSE_Timetable.pdf",
                1,
                "8:30 - 12:30",
                "8:30",
                "12:30",
                "False",
                "False",
            ],
        ],
    )
    write_csv(
        dse_timetable / "practical_speaking.csv",
        [
            "year",
            "date_text_en",
            "date_text_zh",
            "subject_en",
            "subject_zh",
            "component",
            "is_sen",
            "is_tentative",
            "source_file",
            "source_page",
            "time_raw",
            "time_start",
            "time_end",
            "has_listening_reporting_mark",
            "has_approx_end_mark",
        ],
        [[2024, "April", "四月", "English", "英語", "speaking", "False", "False", "x.pdf", 1, "", None, None, "False", "False"]],
    )
    write_csv(
        environment / "air_quality_hourly.csv",
        ["date", "hour", "station", "aqhi", "source_file"],
        [["2024-04-09", 10, "Central", 3.0, "sample.csv"]],
    )
    write_csv(
        environment / "air_quality_daily.csv",
        ["date", "station", "mean_aqhi", "max_aqhi", "hours_reported"],
        [["2024-04-09", "Central", 3.0, 4.0, 12]],
    )
    write_csv(
        environment / "air_quality_daily_city.csv",
        ["date", "mean_aqhi", "max_aqhi", "hours_reported", "stations_reported"],
        [["2024-04-09", 2.5, 4.0, 12, 2]],
    )
    write_csv(
        environment / "wind_direction_daily.csv",
        ["date", "direction_deg", "completeness", "year", "month", "day"],
        [["2024-04-09", 90.0, "C", 2024, 4, 9]],
    )

    monkeypatch.setattr("dse_pollution_corr.paths.processed_dir", lambda: tmp_path)
    monkeypatch.setattr("dse_pollution_corr.paths.environment_processed_dir", lambda: environment)
    monkeypatch.setattr("dse_pollution_corr.db.load_db.processed_dir", lambda: tmp_path)
    monkeypatch.setattr("dse_pollution_corr.db.load_db.environment_processed_dir", lambda: environment)
    return tmp_path


@pytest.fixture
def test_db_path(tmp_path: Path, minimal_processed_tree: Path) -> Path:
    from dse_pollution_corr.db.load_db import rebuild_database

    db_file = tmp_path / "test.duckdb"
    rebuild_database(database_path=db_file)
    return db_file
