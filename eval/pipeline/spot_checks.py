"""Spot-check processed CSVs against manually verified PDF cells."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from dse_pollution_corr.paths import processed_dir


@dataclass(frozen=True)
class EvalCheck:
    name: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class EvalReport:
    suite: str
    checks: list[EvalCheck]

    @property
    def passed(self) -> int:
        return sum(1 for check in self.checks if check.passed)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def score(self) -> float:
        if not self.checks:
            return 1.0
        return self.passed / self.total


def _load(name: str) -> pd.DataFrame:
    return pd.read_csv(processed_dir() / name)


def _row(df: pd.DataFrame, **filters: object) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        mask &= df[column] == value
    matches = df[mask]
    if matches.empty:
        raise KeyError(f"No row matching {filters}")
    return matches.iloc[0]


def run_pipeline_spot_checks() -> EvalReport:
    """Compare processed tables to known values from source PDFs."""
    a = _load("dse_results/category_a_subject_results.csv")
    csd = _load("dse_results/category_a_csd_results.csv")
    b = _load("dse_results/category_b_subject_results.csv")
    c = _load("dse_results/category_c_subject_results.csv")
    w = _load("dse_timetable/written_papers.csv")
    checks: list[EvalCheck] = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        checks.append(EvalCheck(name=name, passed=ok, detail=detail))

    def assert_row(name: str, row: pd.Series, expectations: dict[str, object]) -> None:
        mismatches = {
            field: (row[field], expected)
            for field, expected in expectations.items()
            if row[field] != expected
        }
        if mismatches:
            detail = ", ".join(f"{field}={actual}!={expected}" for field, (actual, expected) in mismatches.items())
            record(name, False, detail)
        else:
            record(name, True)

    cases: list[tuple[str, Callable[[], None]]] = [
        (
            "2022 Biology male",
            lambda: assert_row(
                "2022 Biology male",
                _row(a, year=2022, candidate_type="day_school", subject_en="Biology", gender="male"),
                {"n_entered": 5201, "n_5ss": 156, "pct_5ss": 3.1},
            ),
        ),
        (
            "2022 Biology female",
            lambda: assert_row(
                "2022 Biology female",
                _row(a, year=2022, candidate_type="day_school", subject_en="Biology", gender="female"),
                {"n_entered": 6662, "pct_5ss": 1.5},
            ),
        ),
        (
            "2024 CSD male",
            lambda: assert_row(
                "2024 CSD male",
                _row(csd, year=2024, candidate_type="day_school", gender="male"),
                {"n_attained": 18881, "pct_attained": 92.7},
            ),
        ),
        (
            "2022 Animal Care",
            lambda: assert_row(
                "2022 Animal Care",
                _row(b, year=2022, candidate_type="day_school", subject_en="Animal Care", gender="total"),
                {"n_distinction_ii": 10, "pct_distinction_ii": 18.5},
            ),
        ),
        (
            "2022 French male",
            lambda: assert_row(
                "2022 French male",
                _row(c, year=2022, candidate_type="day_school", subject_en="French Language", gender="male"),
                {"n_a": 4, "pct_a": 22.2},
            ),
        ),
        (
            "2024 Visual Arts",
            lambda: assert_row(
                "2024 Visual Arts",
                _row(w, year=2024, subject_en="Visual Arts"),
                {"exam_date": "2024-04-09", "paper": "1,2"},
            ),
        ),
        (
            "2025 Japanese N1 female",
            lambda: assert_row(
                "2025 Japanese N1 female",
                _row(
                    c,
                    year=2025,
                    candidate_type="day_school",
                    subject_en="Japanese Language",
                    language_proficiency_level="N1",
                    gender="female",
                ),
                {"n_entered": 57, "n_pass": 54, "pct_pass": 94.7},
            ),
        ),
        (
            "2025 Korean total",
            lambda: assert_row(
                "2025 Korean total",
                _row(c, year=2025, candidate_type="day_school", subject_en="Korean Language", gender="total"),
                {"n_entered": 69, "n_pass": 58, "pct_pass": 84.1},
            ),
        ),
    ]

    for name, run_case in cases:
        try:
            run_case()
        except (KeyError, FileNotFoundError, IndexError) as exc:
            record(name, False, str(exc))

    return EvalReport(suite="pipeline", checks=checks)
