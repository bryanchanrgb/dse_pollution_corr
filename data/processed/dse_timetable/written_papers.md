# Written-paper examination timetable

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

