from dse_pollution_corr.agent.charts import build_chart


def test_build_chart_returns_none_for_empty_input() -> None:
    assert build_chart([], []) is None
    assert build_chart(["year"], [[2020]]) is None


def test_build_chart_line_for_year_series() -> None:
    chart = build_chart(
        ["year", "pct_5_plus"],
        [[2019, 10.5], [2020, 11.2], [2021, 12.0]],
    )
    assert chart is not None
    assert chart["type"] == "line"
    assert chart["x_label"] == "year"
    assert chart["y_label"] == "pct_5_plus"
    assert chart["y"] == [10.5, 11.2, 12.0]
