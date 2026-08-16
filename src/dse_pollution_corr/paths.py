"""Project path helpers."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[2]


def raw_dir() -> Path:
    return project_root() / "data" / "raw"


def processed_dir() -> Path:
    return project_root() / "data" / "processed"


def results_pdf_dir() -> Path:
    return raw_dir() / "dse_results"


def timetable_pdf_dir() -> Path:
    return raw_dir() / "dse_timetable"


def environment_raw_dir() -> Path:
    return raw_dir() / "air_quality"


def wind_raw_path() -> Path:
    return raw_dir() / "wind_direction" / "daily_KP_PDIR_ALL.csv"


def environment_processed_dir() -> Path:
    return processed_dir() / "environment"


def db_dir() -> Path:
    return project_root() / "db"


def db_path() -> Path:
    return db_dir() / "dse.duckdb"


def schema_dir() -> Path:
    return db_dir() / "schema"


def catalog_path() -> Path:
    return db_dir() / "catalog.yaml"
