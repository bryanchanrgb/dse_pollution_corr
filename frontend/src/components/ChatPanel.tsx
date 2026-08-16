import { FormEvent, useState } from "react";
import { sendMessage, type ChatResponse } from "../api";
import { ChartView } from "./ChartView";

type Message = {
  role: "user" | "assistant";
  content: string;
  sql?: string | null;
  preview?: ChatResponse["preview"];
  chart?: ChatResponse["chart"];
};

const EXAMPLES = [
  "How did day-school Biology pct_5_plus change from 2019 to 2024?",
  "Which 2022 Category A subjects had the highest pct_u for all candidates?",
  "Show 2024 written exams with city_mean_aqhi on exam day.",
  "Compare average exam-day AQHI with pct_5_plus by subject in 2022.",
];

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latestChart, setLatestChart] = useState<ChatResponse["chart"]>(null);

  async function submit(text: string) {
    const question = text.trim();
    if (!question || loading) return;

    setError(null);
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: question }]);

    try {
      const response = await sendMessage(question);
      setLatestChart(response.chart);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          sql: response.sql,
          preview: response.preview,
          chart: response.chart,
        },
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
    } finally {
      setLoading(false);
      setInput("");
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void submit(input);
  }

  return (
    <div className="layout">
      <section className="panel chat-panel">
        <header className="panel-header">
          <h1>DSE Pollution Analyst</h1>
          <p>Ask questions about exam results, timetables, AQHI, and wind data.</p>
        </header>

        <div className="examples">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              className="example-chip"
              onClick={() => void submit(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>

        <div className="messages">
          {messages.length === 0 && (
            <p className="placeholder">Start with a question or pick an example.</p>
          )}
          {messages.map((message, index) => (
            <article
              key={`${message.role}-${index}`}
              className={`message ${message.role}`}
            >
              <div className="message-label">
                {message.role === "user" ? "You" : "Agent"}
              </div>
              <div className="message-body">{message.content}</div>
              {message.sql && (
                <details className="sql-block">
                  <summary>SQL</summary>
                  <pre>{message.sql}</pre>
                </details>
              )}
              {message.preview && message.preview.rows.length > 0 && (
                <details className="preview-block">
                  <summary>
                    Data preview ({message.preview.row_count} rows)
                  </summary>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          {message.preview.columns.map((col) => (
                            <th key={col}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {message.preview.rows.map((row, rowIndex) => (
                          <tr key={rowIndex}>
                            {row.map((cell, cellIndex) => (
                              <td key={cellIndex}>{String(cell ?? "")}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </details>
              )}
            </article>
          ))}
        </div>

        <form className="composer" onSubmit={onSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="e.g. What was the average city AQHI on 2024 DSE exam days?"
            rows={3}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {loading ? "Analyzing…" : "Ask"}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="panel viz-panel">
        <header className="panel-header">
          <h2>Chart</h2>
        </header>
        <ChartView chart={latestChart} />
      </section>
    </div>
  );
}
