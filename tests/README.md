# Tests

| Suite | Path | Expectation |
|-------|------|-------------|
| Unit | `tests/unit/` | 100% pass — pure logic, in-memory fixtures |
| Integration | `tests/integration/` | 100% pass — DuckDB, API, tool wiring |
| Eval | `eval/` | Scorecard — pipeline/agent quality checks |

## Run

```bash
uv sync --group dev
uv run pytest                    # all tests
uv run pytest tests/unit         # unit only
uv run pytest tests/integration  # integration only
uv run dse-eval                  # eval scorecard
```

## Layout

```
tests/
  unit/dse_pollution_corr/       # mirrors src/
  integration/dse_pollution_corr/
```
