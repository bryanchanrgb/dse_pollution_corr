import pytest

from dse_pollution_corr.db.guardrails import run_query
from dse_pollution_corr.db.load_db import rebuild_database


def test_rebuild_database_loads_tables_and_views(
    tmp_path,
    minimal_processed_tree,
    monkeypatch,
) -> None:
    db_file = tmp_path / "integration.duckdb"
    rebuild_database(database_path=db_file)

    monkeypatch.setattr("dse_pollution_corr.db.guardrails.db_path", lambda: db_file)
    cols, rows = run_query(
        "SELECT year, subject_en, city_mean_aqhi "
        "FROM v_exam_day_environment "
        "WHERE subject_en = 'Visual Arts' "
        "LIMIT 5"
    )
    assert cols == ["year", "subject_en", "city_mean_aqhi"]
    assert rows == [(2024, "Visual Arts", 2.5)]


def test_v_exam_calendar_excludes_reserve_rows(test_db_path, monkeypatch) -> None:
    monkeypatch.setattr("dse_pollution_corr.db.guardrails.db_path", lambda: test_db_path)
    _, rows = run_query(
        "SELECT COUNT(*) FROM v_exam_calendar WHERE COALESCE(is_reserve, FALSE) = TRUE LIMIT 1"
    )
    assert rows[0][0] == 0
