"""Write processed tables and human/agent READMEs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from dse_pollution_corr.paths import processed_dir

_DOCS_DIR = Path(__file__).resolve().parent / "docs"


def _load_doc(name: str) -> str:
    path = _DOCS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8")


def save_processed_tables(tables: dict[str, pd.DataFrame]) -> dict[str, Path]:
    root = processed_dir()
    mapping = {
        "category_a_subject_results": (
            root / "dse_results" / "category_a_subject_results.csv",
            _load_doc("category_a"),
        ),
        "category_a_csd_results": (
            root / "dse_results" / "category_a_csd_results.csv",
            _load_doc("category_a_csd"),
        ),
        "category_b_subject_results": (
            root / "dse_results" / "category_b_subject_results.csv",
            _load_doc("category_b"),
        ),
        "category_c_subject_results": (
            root / "dse_results" / "category_c_subject_results.csv",
            _load_doc("category_c"),
        ),
        "written_papers": (
            root / "dse_timetable" / "written_papers.csv",
            _load_doc("written"),
        ),
        "practical_speaking": (
            root / "dse_timetable" / "practical_speaking.csv",
            _load_doc("practical"),
        ),
    }
    written: dict[str, Path] = {}
    for key, (path, readme) in mapping.items():
        df = tables[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        path.with_name(path.stem + ".md").write_text(readme, encoding="utf-8")
        written[key] = path
    (root / "README.md").write_text(_load_doc("index"), encoding="utf-8")
    return written
