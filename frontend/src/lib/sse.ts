import { API_BASE } from "./api";

export interface SSEEvent {
  event: string;
  data: Record<string, unknown>;
}

/**
 * 发起 POST SSE 请求，逐个回调解析到的事件。
 * 返回一个 abort 函数用于取消连接。
 */
export function connectSSE(
  path: string,
  body: unknown,
  onEvent: (event: SSEEvent) => void,
  onError: (error: Error) => void,
  onDone: () => void,
): () => void {
  const controller = new AbortController();
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;

  (async () => {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "请求失败" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";
      let currentEvent = "";
      let currentData = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            currentData = line.slice(6);
          } else if (line === "") {
            // Empty line = end of event
            if (currentEvent && currentData) {
              try {
                const data = JSON.parse(currentData);
                onEvent({ event: currentEvent, data });
              } catch {
                // skip malformed JSON
              }
            }
            currentEvent = "";
            currentData = "";
          }
        }
      }

      onDone();
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      onError(err instanceof Error ? err : new Error(String(err)));
    }
  })();

  return () => controller.abort();
}
