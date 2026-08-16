import json

import pytest

from dse_pollution_corr.agent.tools import (
    describe_database_object,
    get_last_query_result,
    list_database_objects,
    run_sql_query,
)


def test_list_database_objects_returns_catalog_text() -> None:
    text = list_database_objects.invoke({})
    assert "category_a_subject_results" in text
    assert "v_exam_day_environment" in text


def test_run_sql_query_stores_preview_and_chart(test_db_path, monkeypatch) -> None:
    monkeypatch.setattr("dse_pollution_corr.db.guardrails.db_path", lambda: test_db_path)

    payload = json.loads(
        run_sql_query.invoke(
            {
                "query": (
                    "SELECT year, subject_en, city_mean_aqhi "
                    "FROM v_exam_day_environment "
                    "WHERE subject_en = 'Visual Arts' "
                    "LIMIT 5"
                )
            }
        )
    )
    assert payload["row_count"] == 1
    assert payload["columns"] == ["year", "subject_en", "city_mean_aqhi"]

    last = get_last_query_result()
    assert last is not None
    assert last["sql"] is not None
    assert last["chart"] is None  # chart builder needs 2+ rows


def test_describe_database_object_unknown_name() -> None:
    text = describe_database_object.invoke({"name": "missing_table"})
    assert "Unknown table or view" in text
