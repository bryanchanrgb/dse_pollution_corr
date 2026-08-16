# DSE Pollution Correlation

HKDSE exam results, timetables, and Hong Kong environment data (AQHI + wind), with a SQL agent chat UI.

## Setup

```bash
uv sync
cp .env.example .env   # set OPENROUTER_API_KEY
uv run load-dse-db     # builds db/dse.duckdb (includes environment tables)
cd frontend && npm install
```

## Run

Terminal 1 — API (port 8000):

```bash
uv run dse-api
```

Terminal 2 — React UI (port 5173):

```bash
cd frontend && npm run dev
```

Open http://localhost:5173 and ask questions about exam performance, exam-day AQHI, or wind direction.

## Data pipeline

| Command | Purpose |
|---------|---------|
| `uv run process-dse-pdfs` | PDFs → `data/processed/dse_*` |
| `uv run process-environment` | Raw AQ/wind → `data/processed/environment/` |
| `uv run load-dse-db` | CSVs → DuckDB + analytical views |

Environment tables: `air_quality_hourly`, `air_quality_daily`, `air_quality_daily_city`, `wind_direction_daily`.

Analytical views: `v_exam_calendar`, `v_category_a_performance`, `v_exam_day_environment`, `v_subject_year_aqhi`.

## Testing vs eval

| | `tests/` | `eval/` |
|---|----------|---------|
| Goal | Deterministic correctness | Quality / regression scorecard |
| Pass bar | **100%** | No fixed target |
| Run | `uv sync --group dev && uv run pytest` | `uv run dse-eval` |

After processing PDFs, run `uv run dse-eval` to spot-check output against manually verified PDF cells. Use `--strict` to fail on any missed check (optional CI gate).
