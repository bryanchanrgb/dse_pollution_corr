"""End-to-end processing of raw DSE result and timetable PDFs."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd

from dse_pollution_corr.etl.dse.classify import (
    RESULTS_SCHEMAS,
    SCHEMA_TIMETABLE_PRACTICAL,
    SCHEMA_TIMETABLE_WRITTEN,
    classify_table,
)
from dse_pollution_corr.etl.dse.parsers import parse_results_table
from dse_pollution_corr.etl.dse.parse_timetable import parse_practical_table, parse_written_table
from dse_pollution_corr.etl.dse.pdf_extract import extract_pdf
from dse_pollution_corr.etl.write_outputs import save_processed_tables
from dse_pollution_corr.paths import processed_dir, results_pdf_dir, timetable_pdf_dir


def process_results_pdfs(paths: list[Path] | None = None) -> dict[str, list[dict]]:
    paths = paths or sorted(results_pdf_dir().glob("*.pdf"))
    buckets: dict[str, list[dict]] = defaultdict(list)
    for path in paths:
        doc = extract_pdf(path)
        for page in doc.pages:
            for table in page.tables:
                schema = classify_table(page, table, doc.kind)
                if schema not in RESULTS_SCHEMAS:
                    continue
                rows = parse_results_table(doc, page, table, schema)
                if schema == "category_a_levels":
                    buckets["category_a_subject_results"].extend(rows)
                elif schema == "category_a_csd":
                    buckets["category_a_csd_results"].extend(rows)
                elif schema in {"category_b_standard", "category_b_chinese"}:
                    buckets["category_b_subject_results"].extend(rows)
                elif schema in {"category_c_grades", "category_c_cefr", "category_c_topik"}:
                    buckets["category_c_subject_results"].extend(rows)
    return buckets


def process_timetable_pdfs(paths: list[Path] | None = None) -> dict[str, list[dict]]:
    paths = paths or sorted(timetable_pdf_dir().glob("*.pdf"))
    buckets: dict[str, list[dict]] = defaultdict(list)
    for path in paths:
        doc = extract_pdf(path)
        for page in doc.pages:
            for table in page.tables:
                schema = classify_table(page, table, doc.kind)
                if schema == SCHEMA_TIMETABLE_WRITTEN:
                    buckets["written_papers"].extend(parse_written_table(doc, page, table))
                elif schema == SCHEMA_TIMETABLE_PRACTICAL:
                    buckets["practical_speaking"].extend(parse_practical_table(doc, page, table))
    return buckets


def _frame(rows: list[dict], sort_cols: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    existing = [c for c in sort_cols if c in df.columns]
    return df.sort_values(existing, kind="mergesort").reset_index(drop=True)


def build_tables() -> dict[str, pd.DataFrame]:
    results = process_results_pdfs()
    timetable = process_timetable_pdfs()
    return {
        "category_a_subject_results": _frame(
            results.get("category_a_subject_results", []),
            ["year", "candidate_type", "subject_en", "gender"],
        ),
        "category_a_csd_results": _frame(
            results.get("category_a_csd_results", []),
            ["year", "candidate_type", "gender"],
        ),
        "category_b_subject_results": _frame(
            results.get("category_b_subject_results", []),
            ["year", "candidate_type", "subject_group_en", "subject_en", "gender"],
        ),
        "category_c_subject_results": _frame(
            results.get("category_c_subject_results", []),
            ["year", "candidate_type", "subject_en", "language_proficiency_level", "gender"],
        ),
        "written_papers": _frame(
            timetable.get("written_papers", []),
            ["year", "exam_date", "time_start", "subject_en"],
        ),
        "practical_speaking": _frame(
            timetable.get("practical_speaking", []),
            ["year", "date_text_en", "subject_en"],
        ),
    }


def run(output_dir: Path | None = None) -> dict[str, Path]:
    tables = build_tables()
    written = save_processed_tables(tables)
    if output_dir is not None and output_dir != processed_dir():
        raise ValueError("Custom output_dir is not used; tables are written under data/processed")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Process HKDSE result and timetable PDFs")
    parser.parse_args()
    written = run()
    print(f"Wrote {len(written)} tables under {processed_dir()}")
    for name, path in written.items():
        print(f"  {name}: {path}")
    print("Run `uv run dse-eval` to spot-check processed output.")


if __name__ == "__main__":
    main()
