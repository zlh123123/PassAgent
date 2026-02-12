"use client";

import { useState, useCallback, useRef } from "react";
import { connectSSE } from "@/lib/sse";
import { apiGet } from "@/lib/api";

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

            case "response_chunk":
              setStreamingContent(
                (prev) => prev + (event.data.content as string),
              );
              break;

            case "response_done": {
              // Finalize the assistant message
              setStreamingContent((currentContent) => {
                const msgId = event.data.message_id as string;
                const assistantMsg: ChatMessage = {
                  message_id: msgId,
                  content: currentContent,
                  message_type: "assistant",
                  created_at: new Date().toISOString(),
                  agent_steps: null,
                };
                setMessages((prev) => {
                  // Avoid duplicate message_id
                  if (prev.some((m) => m.message_id === msgId)) return prev;
                  return [...prev, assistantMsg];
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
              setAgentSteps([]);
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

  const stopStreaming = useCallback(() => {
    abortRef.current?.();
    setIsLoading(false);
  }, []);

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
  };
}
