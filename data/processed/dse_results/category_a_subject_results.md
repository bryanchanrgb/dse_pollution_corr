# Category A subject results

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

