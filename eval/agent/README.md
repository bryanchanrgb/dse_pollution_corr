# Agent eval (planned)

Future rubric-based checks for the SQL chat agent, e.g.:

- Does the response cite SQL that was actually run?
- Does a fixed question return rows matching expected filters?
- Is the answer grounded in query results (no invented numbers)?

These are **quality assessments**, not binary pass/fail tests. Run manually or on a schedule with `OPENROUTER_API_KEY` set.
