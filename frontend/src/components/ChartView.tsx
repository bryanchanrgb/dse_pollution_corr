import Plot from "react-plotly.js";
import type { ChartSpec } from "../api";

type Props = {
  chart: ChartSpec | null;
};

export function ChartView({ chart }: Props) {
  if (!chart) {
    return (
      <div className="panel chart-panel empty">
        <p>Chart will appear when the agent returns tabular data.</p>
      </div>
    );
  }

  const trace =
    chart.type === "line"
      ? {
          x: chart.x,
          y: chart.y,
          type: "scatter" as const,
          mode: "lines+markers" as const,
          marker: { color: "#2563eb" },
        }
      : {
          x: chart.x,
          y: chart.y,
          type: "bar" as const,
          marker: { color: "#0f766e" },
        };

  return (
    <div className="panel chart-panel">
      <Plot
        data={[trace]}
        layout={{
          title: chart.title,
          autosize: true,
          margin: { t: 48, r: 24, b: 64, l: 56 },
          xaxis: { title: chart.x_label },
          yaxis: { title: chart.y_label },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
        }}
        useResizeHandler
        style={{ width: "100%", height: "100%" }}
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );
}
