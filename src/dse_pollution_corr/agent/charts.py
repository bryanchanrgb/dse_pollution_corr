"""Build Plotly chart specs from SQL result tables."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def build_chart(
    columns: list[str],
    rows: list[list[Any]],
) -> dict[str, Any] | None:
    if not columns or not rows:
        return None
    df = pd.DataFrame(rows, columns=columns)
    if len(df) < 2:
        return None

    numeric_cols = [c for c in df.columns if _is_numeric(df[c])]
    if not numeric_cols:
        return None

    # Prefer year/date on x-axis
    x_col = None
    for candidate in ("year", "exam_date", "date", "subject_en"):
        if candidate in df.columns:
            x_col = candidate
            break
    if x_col is None:
        x_col = df.columns[0]

    y_col = numeric_cols[0]
    for preferred in ("pct_5_plus", "pct_u", "city_mean_aqhi", "mean_aqhi", "n_sat", "pct_attained"):
        if preferred in numeric_cols:
            y_col = preferred
            break

    if df[x_col].nunique() == len(df) or df[x_col].nunique() >= 2:
        chart_type = "line" if x_col in {"year", "exam_date", "date"} else "bar"
    else:
        chart_type = "bar"

    return {
        "type": chart_type,
        "title": f"{y_col} by {x_col}",
        "x": df[x_col].astype(str).tolist(),
        "y": df[y_col].tolist(),
        "x_label": x_col,
        "y_label": y_col,
        "rows": df.to_dict(orient="records")[:100],
    }
