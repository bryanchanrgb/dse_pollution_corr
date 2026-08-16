# Category B (Applied Learning) subject results

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

