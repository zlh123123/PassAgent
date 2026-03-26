"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { connectSSE } from "@/lib/sse";
import { apiGet, apiPost, apiDelete } from "@/lib/api";

export interface ChatMessage {
  message_id: string;
  content: string;
  message_type: "human" | "assistant";
  created_at: string;
  feedback?: { feedback_type: "like" | "dislike" } | null;
  agent_steps?: AgentStep[] | null;
}

export interface AgentStep {
  step?: number;
  node: string;
  action?: string;
  reasoning?: string;
  summary?: Record<string, unknown>;
}

interface MessagesResponse {
  messages: ChatMessage[];
}

export function useChat(sessionId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [queuePosition, setQueuePosition] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState("");
  const abortRef = useRef<(() => void) | null>(null);
  const currentTaskIdRef = useRef<string | null>(null);
  const prevSessionIdRef = useRef<string | null>(null);

  const fetchMessages = useCallback(async () => {
    if (!sessionId) return;
    try {
      const res = await apiGet<MessagesResponse>(
        `/api/sessions/${sessionId}/messages`,
      );
      setMessages(res.messages);
    } catch (err) {
      console.error("Failed to fetch messages:", err);
    }
  }, [sessionId]);

  // 当 sessionId 变化时，清理当前状态并重新加载消息
  useEffect(() => {
    if (prevSessionIdRef.current !== sessionId) {
      // sessionId 变化，清理之前的状态
      if (prevSessionIdRef.current !== null) {
        // 停止之前的流式传输
        abortRef.current?.();
        currentTaskIdRef.current = null;
      }

      // 清理状态
      setMessages([]);
      setIsLoading(false);
      setAgentSteps([]);
      setQueuePosition(null);
      setError(null);
      setStreamingContent("");

      // 更新 prevSessionId
      prevSessionIdRef.current = sessionId;

      // 加载新对话的消息
      if (sessionId) {
        fetchMessages();
      }
    }
  }, [sessionId, fetchMessages]);

  const sendMessage = useCallback(
    (content: string, fileIds: string[] = []) => {
      if (!sessionId || isLoading) return;

      setIsLoading(true);
      setError(null);
      setAgentSteps([]);
      setQueuePosition(null);
      setStreamingContent("");

      // Optimistically add user message
      const userMsg: ChatMessage = {
        message_id: `temp-${Date.now()}`,
        content,
        message_type: "human",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      const abort = connectSSE(
        `/api/chat/${sessionId}`,
        { message: content, file_ids: fileIds },
        (event) => {
          switch (event.event) {
            case "task_queued":
              currentTaskIdRef.current = event.data.task_id as string;
              setQueuePosition(event.data.position as number);
              break;

            case "task_started":
              setQueuePosition(null);
              break;

            case "agent_step":
              setAgentSteps((prev) => [
                ...prev,
                event.data as unknown as AgentStep,
              ]);
              break;

            case "passinfinity_open":
              window.dispatchEvent(
                new CustomEvent("passinfinity-open", {
                  detail: event.data,
                }),
              );
              break;

            case "response_chunk":
              setStreamingContent(
                (prev) => prev + (event.data.content as string),
              );
              break;

            case "response_done": {
              // Finalize the assistant message
              setStreamingContent((currentContent) => {
                const msgId = event.data.message_id as string;
                setAgentSteps((currentSteps) => {
                  const assistantMsg: ChatMessage = {
                    message_id: msgId,
                    content: currentContent,
                    message_type: "assistant",
                    created_at: new Date().toISOString(),
                    agent_steps: currentSteps.length > 0 ? currentSteps : null,
                  };
                  setMessages((prev) => {
                    if (prev.some((m) => m.message_id === msgId)) return prev;
                    return [...prev, assistantMsg];
                  });
                  return [];
                });
                return "";
              });
              break;
            }

            case "task_failed":
              setError(event.data.error as string);
              break;

            case "done":
              setIsLoading(false);
              currentTaskIdRef.current = null;
              // Trigger custom event to notify session list should be refreshed
              window.dispatchEvent(new CustomEvent("session-updated"));
              break;

            case "task_cancelled":
              setError(event.data.message as string || "任务已停止");
              break;
          }
        },
        (err) => {
          setError(err.message);
          setIsLoading(false);
        },
        () => {
          setIsLoading(false);
        },
      );

      abortRef.current = abort;
    },
    [sessionId, isLoading],
  );

  const stopStreaming = useCallback(async () => {
    // 如果有 task_id，先调用后端停止 API（在关闭 SSE 前）
    const taskId = currentTaskIdRef.current;
    if (taskId) {
      try {
        await apiPost(`/api/chat/${taskId}/stop`, {});
      } catch (err: any) {
        // 忽略 404 错误（任务已完成），其他错误记录日志
        if (err?.status !== 404) {
          console.error("Failed to stop task:", err);
        }
      }
      currentTaskIdRef.current = null;
    }

    // 然后再关闭 SSE 连接
    abortRef.current?.();
    setIsLoading(false);
  }, []);

  const toggleFeedback = useCallback(
    async (messageId: string, feedbackType: "like" | "dislike") => {
      try {
        await apiPost(`/api/messages/${messageId}/feedback`, {
          feedback_type: feedbackType,
        });
        setMessages((prev) =>
          prev.map((m) => {
            if (m.message_id !== messageId) return m;
            // Toggle: if same type, remove; otherwise set new type
            const current = m.feedback?.feedback_type;
            if (current === feedbackType) {
              return { ...m, feedback: null };
            }
            return { ...m, feedback: { feedback_type: feedbackType } };
          }),
        );
      } catch (err) {
        console.error("Failed to toggle feedback:", err);
      }
    },
    [],
  );

  const retryMessage = useCallback(
    async (assistantMessageId: string) => {
      if (!sessionId || isLoading) return;
      // Find the user message right before this assistant message
      const idx = messages.findIndex(
        (m) => m.message_id === assistantMessageId,
      );
      if (idx <= 0) return;
      const userMsg = messages[idx - 1];
      if (userMsg.message_type !== "human") return;

      // Delete the assistant message from backend
      try {
        await apiDelete(`/api/messages/${assistantMessageId}`);
      } catch {
        // ignore if already deleted
      }
      // Remove it from local state
      setMessages((prev) =>
        prev.filter((m) => m.message_id !== assistantMessageId),
      );
      // Resend the user message
      sendMessage(userMsg.content);
    },
    [sessionId, isLoading, messages, sendMessage],
  );

  return {
    messages,
    setMessages,
    isLoading,
    agentSteps,
    queuePosition,
    error,
    streamingContent,
    fetchMessages,
    sendMessage,
    stopStreaming,
    toggleFeedback,
    retryMessage,
  };
}
