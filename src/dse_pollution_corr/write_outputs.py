"""Write processed tables and human/agent READMEs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .paths import processed_dir

README_CATEGORY_A = """# Category A subject results

## What this table is

One row per **year × candidate population × subject × gender** from HKEAA Table 5a (day-school candidates) and Table 5b (all candidates).

Category A is the NSS subject set (Chinese Language, English Language, Mathematics, electives, etc.).

## How to read a row

- `candidate_type`: `day_school` (日校考生) or `all` (全體考生).
- `gender`: `male`, `female`, or `total`. Subject names from merged cells are copied onto every gender row.
- `subject_group_en` / `subject_group_zh`: parent label when the PDF groups papers (BAFS, Mathematics, Combined/Integrated Science, Technology and Living). Null for standalone subjects.
- `subject_en` / `subject_zh`: the paper reported in that block. Mathematics parts are prefixed with "Mathematics" / "數學".
- `is_summary`: true for "All Category A subjects" and similar totals. HKEAA treats Mathematics Compulsory and Extended Parts as one subject when building that total (the better result is kept).
- `n_entered`, `n_sat`: candidates entered / sat.
- `chinese_version_pct`: share of sitting candidates who chose the Chinese paper. Null / missing when the subject is Chinese-only (shown as "-" in the PDF).
- Grade columns come in pairs. The PDF stacks a **count** on a **cumulative percentage** in one cell; those are split here:
  - `n_5ss` / `pct_5ss`: level 5**
  - `n_5s_plus` / `pct_5s_plus`: level 5* **or above**
  - `n_5_plus` … `n_1_plus`: that level **or above**
  - `n_u` / `pct_u`: unclassified (below level 1). Not printed on the certificate.
- Percentages are stored as 0–100 (e.g. `3.1` means 3.1%), matching the PDF.

## What is not in this file

Citizenship and Social Development (2024–) is graded Attained / Unattained, not 5**–1. Those rows are in `category_a_csd_results.csv`.
"""

README_CATEGORY_A_CSD = """# Category A — Citizenship and Social Development

## What this table is

Citizenship and Social Development (公民與社會發展) replaced Liberal Studies from 2024. HKEAA still prints it under Table 5a/5b, but the scale is **Attained / Unattained**, not the five-level scale used by other Category A subjects.

One row per **year × candidate population × gender**.

## How to read a row

- `n_entered`, `n_sat`, `chinese_version_pct`: same meaning as other Category A tables.
- `n_attained` / `pct_attained`: candidates awarded Attained.
- `n_unattained` / `pct_unattained`: candidates who did not attain. Unattained is not recorded on the certificate.
- Percentages are 0–100 and are relative to `n_sat`.
- Merged subject cells are copied onto male, female, and total rows.
"""

README_CATEGORY_B = """# Category B (Applied Learning) subject results

## What this table is

One row per **year × candidate population × Applied Learning subject × gender** from Table 5c (day school) and Table 5d (all candidates).

Assessment is done by course providers and moderated by HKEAA.

## How to read a row

- `subject_group_en` / `subject_group_zh`: Applied Learning area (Applied Science, Services, etc.). Copied onto every subject in that area.
- `n_entered`: candidates entered.
- `n_fulfilled_attendance`: candidates who met the attendance requirement and can be graded. Percentages use this denominator.
- `grading_scheme`:
  - `apl_standard` — most ApL subjects: Distinction (II), Distinction (I) or above, Attained or above, Unattained.
  - `apl_chinese` — Applied Learning Chinese (for non-Chinese speaking students): Distinction, Attained or above, Unattained (no I/II split).
- Count/percentage pairs:
  - `n_distinction_ii` / `pct_distinction_ii`
  - `n_distinction_i_or_above` / `pct_distinction_i_or_above` (cumulative)
  - `n_distinction` / `pct_distinction` (ApL Chinese only)
  - `n_attained_or_above` / `pct_attained_or_above` (cumulative)
  - `n_unattained` / `pct_unattained`
- Unused scheme columns are null.
- `is_summary`: true for "All Category B subjects (except Applied Learning Chinese)" and the ApL Chinese total row.
- Percentages are 0–100.
"""

README_CATEGORY_C = """# Category C (Other Languages) subject results

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
"""

README_WRITTEN = """# Written-paper examination timetable

## What this table is

One row per **year × exam sitting** from the main HKDSE written-paper timetable.

Merged date cells are copied onto every paper that day. When one PDF row listed two papers and two time ranges in the same cells, it is exploded into two rows.

## How to read a row

- `exam_date`: ISO date when it could be parsed from the English or Chinese date text.
- `date_text_en` / `date_text_zh`: original date labels (useful when the PDF only gives a weekday continuation line).
- `time_start` / `time_end`: 24-hour clock. `time_raw` keeps the original string.
- `has_listening_reporting_mark`: the PDF marked the slot with `#` (listening paper reporting-time footnote).
- `has_approx_end_mark`: the PDF marked the slot with `*` (approximate end time for listening / integrated skills).
- `subject_en` / `subject_zh`: subject name with the paper number removed when it could be parsed.
- `paper`: paper code (`1`, `2`, `1,2`, `3`, `1A`, `1B`, `Modules 1,2`, …). Visual Arts taken as a single sitting is `1,2`.
- `is_reserve`: reserve / 後備 day with no paper scheduled.
"""

README_PRACTICAL = """# Practical and speaking examination timetable

## What this table is

One row per **year × practical or speaking component** from the smaller timetable at the bottom of each HKDSE timetable PDF.

These components run over a date range, not a single written-paper sitting.

## How to read a row

- `date_text_en` / `date_text_zh`: period as printed (e.g. "mid-February – early April 2024"). Merged or split bilingual date lines are combined.
- `time_start` / `time_end`: session window when printed.
- `subject_en` / `subject_zh`: component name.
- `component`: `practical` or `speaking` when that could be inferred.
- `is_sen`: SEN / 特殊需要考生 session.
- `is_tentative`: PDF marked the dates as tentative / 暫定.
"""

README_INDEX = """# Processed DSE tables

Structured relational extracts from HKEAA Table 5 subject-result PDFs (`data/raw/dse_results`) and annual examination timetables (`data/raw/dse_timetable`).

| File | Source | Grain |
| --- | --- | --- |
| `dse_results/category_a_subject_results.csv` | Tables 5a–5b, 5-level subjects | year × population × subject × gender |
| `dse_results/category_a_csd_results.csv` | Tables 5a–5b, Citizenship and Social Development (2024–) | year × population × gender |
| `dse_results/category_b_subject_results.csv` | Tables 5c–5d, Applied Learning | year × population × subject × gender |
| `dse_results/category_c_subject_results.csv` | Tables 5e–5f, Other Languages | year × population × subject × (level) × gender |
| `dse_timetable/written_papers.csv` | Main timetable | year × sitting |
| `dse_timetable/practical_speaking.csv` | Practical / speaking block | year × component |

Each folder has a README next to the CSV describing columns and PDF conventions (merged cells, cumulative grades, count vs percentage).

Regenerate with:

```
uv run process-dse-pdfs
```
"""


def save_processed_tables(tables: dict[str, pd.DataFrame]) -> dict[str, Path]:
    root = processed_dir()
    mapping = {
        "category_a_subject_results": (
            root / "dse_results" / "category_a_subject_results.csv",
            README_CATEGORY_A,
        ),
        "category_a_csd_results": (
            root / "dse_results" / "category_a_csd_results.csv",
            README_CATEGORY_A_CSD,
        ),
        "category_b_subject_results": (
            root / "dse_results" / "category_b_subject_results.csv",
            README_CATEGORY_B,
        ),
        "category_c_subject_results": (
            root / "dse_results" / "category_c_subject_results.csv",
            README_CATEGORY_C,
        ),
        "written_papers": (
            root / "dse_timetable" / "written_papers.csv",
            README_WRITTEN,
        ),
        "practical_speaking": (
            root / "dse_timetable" / "practical_speaking.csv",
            README_PRACTICAL,
        ),
    }
    written: dict[str, Path] = {}
    for key, (path, readme) in mapping.items():
        df = tables[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        path.with_name(path.stem + ".md").write_text(readme.lstrip() + "\n", encoding="utf-8")
        written[key] = path
    (root / "README.md").write_text(README_INDEX.lstrip() + "\n", encoding="utf-8")
    return written
