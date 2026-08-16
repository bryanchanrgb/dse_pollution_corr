# Processed DSE tables

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

