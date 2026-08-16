"""Run eval suites and print scorecards."""

from __future__ import annotations

import argparse
from typing import Callable

from eval.pipeline.spot_checks import EvalReport, run_pipeline_spot_checks

SUITES: dict[str, Callable[[], EvalReport]] = {
    "pipeline": run_pipeline_spot_checks,
}


def _print_report(report: EvalReport) -> None:
    print(f"\n[{report.suite}] {report.passed}/{report.total} passed ({report.score:.0%})")
    for check in report.checks:
        mark = "ok" if check.passed else "FAIL"
        line = f"  [{mark}] {check.name}"
        if check.detail:
            line += f" — {check.detail}"
        print(line)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run DSE pollution correlation eval suites")
    parser.add_argument(
        "--suite",
        choices=[*SUITES.keys(), "all"],
        default="all",
        help="Eval suite to run (default: all)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any check fails (default: always exit 0)",
    )
    args = parser.parse_args(argv)

    suite_names = list(SUITES.keys()) if args.suite == "all" else [args.suite]
    reports = [SUITES[name]() for name in suite_names]

    total_passed = sum(report.passed for report in reports)
    total_checks = sum(report.total for report in reports)
    for report in reports:
        _print_report(report)

    print(f"\nOverall: {total_passed}/{total_checks} checks passed")
    if args.strict and total_passed < total_checks:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
