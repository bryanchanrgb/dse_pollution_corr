from pathlib import Path

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTO_BUILD_DB", "false")
    from dse_pollution_corr.api.main import app

    return TestClient(app)


def test_health_reports_database_presence(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("dse_pollution_corr.api.main.db_path", lambda: __import__("pathlib").Path("/tmp/missing.duckdb"))
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "False"


def test_chat_returns_mocked_agent_payload(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_file = tmp_path / "test.duckdb"
    db_file.write_text("duckdb", encoding="utf-8")
    monkeypatch.setattr("dse_pollution_corr.api.main.db_path", lambda: db_file)

    mocked = {
        "answer": "Biology pct_5_plus was 10%.",
        "sql": "SELECT 1 LIMIT 5",
        "chart": None,
        "preview": {"columns": ["pct_5_plus"], "rows": [[10.0]], "row_count": 1},
    }
    with patch("dse_pollution_corr.api.main.run_agent", return_value=mocked):
        response = client.post("/api/chat", json={"message": "How did Biology do?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == mocked["answer"]
    assert body["sql"] == mocked["sql"]
    assert body["preview"]["row_count"] == 1


def test_chat_returns_503_when_database_missing(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing = tmp_path / "missing.duckdb"
    monkeypatch.setattr("dse_pollution_corr.api.main.db_path", lambda: missing)
    response = client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 503
