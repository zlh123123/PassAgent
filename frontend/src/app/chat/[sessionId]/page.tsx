"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "@/components/chat/message-list";
import { MessageItem, StreamingMessage, TypingIndicator } from "@/components/chat/message-item";
import { AgentSteps } from "@/components/chat/agent-steps";
import { QueueStatus } from "@/components/chat/queue-status";
import { ChatInput } from "@/components/chat/chat-input";

export default function SessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const {
    messages,
    isLoading,
    agentSteps,
    queuePosition,
    error,
    streamingContent,
    fetchMessages,
    sendMessage,
    stopStreaming,
  } = useChat(sessionId);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  return (
    <>
      <MessageList>
        {messages.map((msg) => (
          <MessageItem key={msg.message_id} message={msg} />
        ))}

        <QueueStatus position={queuePosition} />

        {agentSteps.length > 0 && (
          <AgentSteps steps={agentSteps} isStreaming={isLoading} />
        )}

        {streamingContent && <StreamingMessage content={streamingContent} />}

        {isLoading && !streamingContent && agentSteps.length === 0 && queuePosition === null && (
          <TypingIndicator />
        )}

        {error && (
          <div className="flex justify-center">
            <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 px-4 py-2 text-sm text-red-600 dark:text-red-400">
              {error}
            </div>
          </div>
        )}
      </MessageList>

      <ChatInput
        onSend={sendMessage}
        isLoading={isLoading}
        onStop={stopStreaming}
      />
    </>
  );
}
