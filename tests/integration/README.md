# Integration tests

Cross-module tests using temp DuckDB, FastAPI TestClient, or other real subsystems. Still deterministic with a **100% pass expectation**.

## Run

```bash
uv run pytest tests/integration
uv run pytest   # unit + integration
```

## Layout

```
tests/integration/
  conftest.py              # minimal_processed_tree, test_db_path
  dse_pollution_corr/
    db/test_load_db.py
    agent/test_tools.py
    api/test_main.py
```
