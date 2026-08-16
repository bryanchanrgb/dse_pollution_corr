"""Process raw air quality and wind direction files into relational CSVs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from dse_pollution_corr.paths import (
    environment_processed_dir,
    environment_raw_dir,
    wind_raw_path,
)

META_COLS = {"Date", "Hour", "file_name"}


def _parse_aqhi(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().replace("*", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def read_air_quality_file(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=7)
    df["Date"] = df["Date"].ffill()
    df["Hour"] = pd.to_numeric(df["Hour"], errors="coerce")
    station_cols = [c for c in df.columns if c not in META_COLS]
    long_df = df.melt(
        id_vars=["Date", "Hour"],
        value_vars=station_cols,
        var_name="station",
        value_name="aqhi_raw",
    )
    long_df["aqhi"] = long_df["aqhi_raw"].map(_parse_aqhi)
    long_df = long_df.drop(columns=["aqhi_raw"])
    long_df["date"] = pd.to_datetime(long_df["Date"], errors="coerce").dt.date
    long_df["hour"] = long_df["Hour"].astype("Int64")
    long_df["source_file"] = path.name
    return long_df[["date", "hour", "station", "aqhi", "source_file"]]


def process_air_quality() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    for path in sorted(environment_raw_dir().glob("*.csv")):
        frames.append(read_air_quality_file(path))
    hourly = pd.concat(frames, ignore_index=True)
    hourly = hourly.dropna(subset=["date"])

    daily = (
        hourly.dropna(subset=["aqhi"])
        .groupby(["date", "station"], as_index=False)
        .agg(
            mean_aqhi=("aqhi", "mean"),
            max_aqhi=("aqhi", "max"),
            hours_reported=("aqhi", "count"),
        )
    )
    city_daily = (
        hourly.dropna(subset=["aqhi"])
        .groupby("date", as_index=False)
        .agg(
            mean_aqhi=("aqhi", "mean"),
            max_aqhi=("aqhi", "max"),
            hours_reported=("aqhi", "count"),
            stations_reported=("station", "nunique"),
        )
    )
    return hourly, daily, city_daily


def process_wind_direction() -> pd.DataFrame:
    df = pd.read_csv(wind_raw_path(), skiprows=2)
    df.columns = ["year", "month", "day", "direction_deg", "completeness"]
    df["date"] = pd.to_datetime(
        dict(year=df["year"], month=df["month"], day=df["day"]),
        errors="coerce",
    ).dt.date
    df["direction_deg"] = pd.to_numeric(df["direction_deg"], errors="coerce")
    df["completeness"] = df["completeness"].astype(str).str.strip()
    return df[["date", "direction_deg", "completeness", "year", "month", "day"]]


def write_environment_tables(output_dir: Path | None = None) -> dict[str, Path]:
    output_dir = output_dir or environment_processed_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    hourly, daily, city_daily = process_air_quality()
    wind = process_wind_direction()

    paths = {
        "air_quality_hourly": output_dir / "air_quality_hourly.csv",
        "air_quality_daily": output_dir / "air_quality_daily.csv",
        "air_quality_daily_city": output_dir / "air_quality_daily_city.csv",
        "wind_direction_daily": output_dir / "wind_direction_daily.csv",
    }
    hourly.to_csv(paths["air_quality_hourly"], index=False)
    daily.to_csv(paths["air_quality_daily"], index=False)
    city_daily.to_csv(paths["air_quality_daily_city"], index=False)
    wind.to_csv(paths["wind_direction_daily"], index=False)

    readme = output_dir / "README.md"
    readme.write_text(
        """# Environment tables

## air_quality_hourly
One row per date × hour × monitoring station. `aqhi` is the Air Quality Health Index (1–10+).

## air_quality_daily
Daily mean/max AQHI per station.

## air_quality_daily_city
City-wide daily mean/max AQHI (average across stations with readings that day). Use this to join exam dates.

## wind_direction_daily
Daily prevailing wind direction (degrees) at King's Park. `completeness` is `C` (complete) or `#` (partial).
""",
        encoding="utf-8",
    )
    return paths


def main() -> None:
    paths = write_environment_tables()
    for name, path in paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
