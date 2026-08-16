# Eval

Evaluations assess **quality and regression** against real pipeline output or live services. They are informative, not gating: a partial score is expected and useful.

| | `tests/` | `eval/` |
|---|----------|---------|
| Purpose | Correctness of deterministic logic | End-to-end quality / regression |
| Pass expectation | **100%** — any failure is a bug | **No fixed target** — score informs review |
| CI default | Run on every commit | Optional; use `--strict` to gate |
| Dependencies | In-memory fixtures | Processed CSVs, PDFs, API keys |

## Suites

| Suite | Command | Requires |
|-------|---------|----------|
| Pipeline spot checks | `uv run dse-eval --suite pipeline` | `data/processed/` from `process-dse-pdfs` |

Future: `eval/agent/` for LLM answer/SQL quality rubrics (manual or weekly).

## Usage

```bash
uv run process-dse-pdfs          # generate processed CSVs first
uv run dse-eval                  # print scorecard, exit 0
uv run dse-eval --strict         # exit 1 if any check fails
uv run dse-eval --suite pipeline
```
