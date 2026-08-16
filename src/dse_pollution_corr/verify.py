"""Spot-check structured tables against known PDF cells."""

from __future__ import annotations

import pandas as pd

from .paths import processed_dir


def _load(name: str) -> pd.DataFrame:
    return pd.read_csv(processed_dir() / name)


def run_checks() -> list[str]:
    a = _load("dse_results/category_a_subject_results.csv")
    csd = _load("dse_results/category_a_csd_results.csv")
    b = _load("dse_results/category_b_subject_results.csv")
    c = _load("dse_results/category_c_subject_results.csv")
    w = _load("dse_timetable/written_papers.csv")
    failures: list[str] = []

    def check(name: str, cond: bool, detail: object = "") -> None:
        if not cond:
            failures.append(f"{name}: {detail}")

    bio_m = a[
        (a.year == 2022)
        & (a.candidate_type == "day_school")
        & (a.subject_en == "Biology")
        & (a.gender == "male")
    ].iloc[0]
    check("2022 Biology male", bio_m.n_entered == 5201 and bio_m.n_5ss == 156 and bio_m.pct_5ss == 3.1)

    bio_f = a[
        (a.year == 2022)
        & (a.candidate_type == "day_school")
        & (a.subject_en == "Biology")
        & (a.gender == "female")
    ].iloc[0]
    check("2022 Biology female", bio_f.n_entered == 6662 and bio_f.pct_5ss == 1.5)

    csd_m = csd[
        (csd.year == 2024) & (csd.candidate_type == "day_school") & (csd.gender == "male")
    ].iloc[0]
    check("2024 CSD male", csd_m.n_attained == 18881 and csd_m.pct_attained == 92.7)

    animal = b[
        (b.year == 2022)
        & (b.candidate_type == "day_school")
        & (b.subject_en == "Animal Care")
        & (b.gender == "total")
    ].iloc[0]
    check("2022 Animal Care", animal.n_distinction_ii == 10 and animal.pct_distinction_ii == 18.5)

    french = c[
        (c.year == 2022)
        & (c.candidate_type == "day_school")
        & (c.subject_en == "French Language")
        & (c.gender == "male")
    ].iloc[0]
    check("2022 French male", french.n_a == 4 and french.pct_a == 22.2)

    va = w[(w.year == 2024) & (w.subject_en == "Visual Arts")].iloc[0]
    check("2024 Visual Arts", va.exam_date == "2024-04-09" and va.paper == "1,2")

    jp = c[
        (c.year == 2025)
        & (c.candidate_type == "day_school")
        & (c.subject_en == "Japanese Language")
        & (c.language_proficiency_level == "N1")
        & (c.gender == "female")
    ].iloc[0]
    check("2025 Japanese N1 female", jp.n_entered == 57 and jp.n_pass == 54 and jp.pct_pass == 94.7)

    kr = c[
        (c.year == 2025)
        & (c.candidate_type == "day_school")
        & (c.subject_en == "Korean Language")
        & (c.gender == "total")
    ].iloc[0]
    check("2025 Korean total", kr.n_entered == 69 and kr.n_pass == 58 and kr.pct_pass == 84.1)
    return failures


def main() -> None:
    failures = run_checks()
    if failures:
        print("Verification failed:")
        for item in failures:
            print(" ", item)
        raise SystemExit(1)
    print("Verification passed")


if __name__ == "__main__":
    main()
