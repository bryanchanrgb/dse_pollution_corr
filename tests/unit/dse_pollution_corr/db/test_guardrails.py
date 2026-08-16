import pytest

from dse_pollution_corr.db.guardrails import validate_sql


@pytest.mark.parametrize(
    ("sql", "fragment"),
    [
        ("SELECT 1", "LIMIT 500"),
        ("SELECT * FROM t LIMIT 10", "LIMIT 10"),
        ("  select year from v_exam_calendar  ", "LIMIT 500"),
        ("WITH x AS (SELECT 1 AS n) SELECT n FROM x", "LIMIT 500"),
    ],
)
def test_validate_sql_accepts_select(sql: str, fragment: str) -> None:
    result = validate_sql(sql)
    assert fragment in result


@pytest.mark.parametrize(
    "sql",
    [
        "",
        "INSERT INTO t VALUES (1)",
        "DROP TABLE t",
        "SELECT 1; SELECT 2",
        "PRAGMA table_info('t')",
    ],
)
def test_validate_sql_rejects_unsafe(sql: str) -> None:
    with pytest.raises(ValueError):
        validate_sql(sql)
