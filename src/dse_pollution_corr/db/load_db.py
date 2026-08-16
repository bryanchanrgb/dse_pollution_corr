"""Load processed CSVs into DuckDB."""

from __future__ import annotations

from pathlib import Path

import duckdb

from dse_pollution_corr.etl.environment.process_environment import write_environment_tables
from dse_pollution_corr.paths import (
    db_dir,
    db_path,
    environment_processed_dir,
    processed_dir,
    schema_dir,
)


def _register_csv(conn: duckdb.DuckDBPyConnection, table: str, csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV for {table}: {csv_path}")
    conn.execute(
        f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto(?)",
        [str(csv_path)],
    )


def _apply_sql_file(conn: duckdb.DuckDBPyConnection, path: Path) -> None:
    conn.execute(path.read_text(encoding="utf-8"))


def rebuild_database(
    *,
    skip_environment: bool = False,
    database_path: Path | None = None,
) -> Path:
    database_path = database_path or db_path()
    db_dir().mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()

    if not skip_environment:
        write_environment_tables()

    conn = duckdb.connect(str(database_path))
    try:
        dse_results = processed_dir() / "dse_results"
        dse_timetable = processed_dir() / "dse_timetable"
        env = environment_processed_dir()

        tables = {
            "category_a_subject_results": dse_results / "category_a_subject_results.csv",
            "category_a_csd_results": dse_results / "category_a_csd_results.csv",
            "category_b_subject_results": dse_results / "category_b_subject_results.csv",
            "category_c_subject_results": dse_results / "category_c_subject_results.csv",
            "written_papers": dse_timetable / "written_papers.csv",
            "practical_speaking": dse_timetable / "practical_speaking.csv",
            "air_quality_hourly": env / "air_quality_hourly.csv",
            "air_quality_daily": env / "air_quality_daily.csv",
            "air_quality_daily_city": env / "air_quality_daily_city.csv",
            "wind_direction_daily": env / "wind_direction_daily.csv",
        }
        for name, csv_path in tables.items():
            _register_csv(conn, name, csv_path)

        views_sql = schema_dir() / "002_views.sql"
        if views_sql.exists():
            _apply_sql_file(conn, views_sql)
    finally:
        conn.close()
    return database_path


def main() -> None:
    path = rebuild_database()
    print(f"Built database at {path}")


if __name__ == "__main__":
    main()
