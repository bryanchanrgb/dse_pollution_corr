# Category C (Other Languages) subject results

## What this table is

One row per **year × candidate population × language subject × (proficiency level) × gender** from Table 5e (day school) and Table 5f (all candidates).

HKEAA changed the Category C reporting scale in 2025.

## Grading schemes

`grading_scheme = cambridge_grades` (2019–2024):
- Cambridge-style cumulative grades: `a`, `b+`, `c+`, `d+`, `e+`, and `U`.
- `language_proficiency_level` is null.
- `n_sat` is candidates who sat.
- Pass/fail columns are null.

`grading_scheme = cefr_pass_fail` (2025 French / German / Spanish):
- Results are reported by CEFR level (`C2`, `C1`, `B2`, `B1`, `A2`) plus a `Subtotal` row.
- `n_sat` is "number of candidates with results submitted".
- `n_pass` / `pct_pass` and `n_not_pass` / `pct_not_pass`.
- Cambridge grade columns are null.
- Zero-entry levels are kept; the PDF shows "-" for pass/fail in those rows, stored as null.

`grading_scheme = jlpt_pass_fail` (2025 Japanese):
- Same pass/fail layout, but levels are JLPT `N1`, `N2`, `N3` plus `Subtotal`.

`grading_scheme = topik_grades` (2025 Korean):
- `language_proficiency_level` is `TOPIK II`.
- Count/percentage pairs for `grade_6` … `grade_3`, plus `pass_subtotal` (小計, treated as pass) and `n_not_pass`.

`grading_scheme = pass_fail` (2025 "All Category C subjects" summary):
- No proficiency level. Overall pass / not pass only.

## Other fields

- Merged subject (and 2025 proficiency-level) cells are copied onto every gender row.
- `is_summary`: true for "All Category C subjects".
- Percentages are 0–100.

