export type ChartSpec = {
  type: "line" | "bar";
  title: string;
  x: string[];
  y: number[];
  x_label: string;
  y_label: string;
  rows?: Record<string, unknown>[];
};

export type TablePreview = {
  columns: string[];
  rows: unknown[][];
  row_count: number;
};

export type ChatResponse = {
  answer: string;
  sql: string | null;
  chart: ChartSpec | null;
  preview: TablePreview | null;
};

export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json();
}
