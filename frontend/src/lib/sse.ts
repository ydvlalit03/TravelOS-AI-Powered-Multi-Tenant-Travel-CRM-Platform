/** Consume a Server-Sent-Events stream from a POST endpoint (with auth). */
import { tokenStore } from "./api";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function streamSSE(
  path: string,
  body: unknown,
  onEvent: (event: Record<string, unknown>) => void,
): Promise<void> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(tokenStore.access ? { Authorization: `Bearer ${tokenStore.access}` } : {}),
    },
    body: JSON.stringify(body),
  });
  if (!resp.ok || !resp.body) {
    throw new Error(`Stream failed (${resp.status})`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const chunk = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const line = chunk.split("\n").find((l) => l.startsWith("data: "));
      if (line) {
        try {
          onEvent(JSON.parse(line.slice(6)));
        } catch {
          /* ignore malformed event */
        }
      }
    }
  }
}
