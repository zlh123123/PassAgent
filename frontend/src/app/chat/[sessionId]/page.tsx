"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "@/components/chat/message-list";
import { MessageItem, StreamingMessage, TypingIndicator } from "@/components/chat/message-item";
import { AgentSteps } from "@/components/chat/agent-steps";
import { QueueStatus } from "@/components/chat/queue-status";
import { ChatInput } from "@/components/chat/chat-input";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";

interface PassInfinityOpenDetail {
  path?: string;
  title?: string;
  description?: string;
  instructions?: string[];
}

export default function SessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();
  const [pendingOpen, setPendingOpen] = useState<PassInfinityOpenDetail | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const {
    messages,
    isLoading,
    agentSteps,
    queuePosition,
    error,
    streamingContent,
    sendMessage,
    stopStreaming,
    toggleFeedback,
    retryMessage,
  } = useChat(sessionId);

  useEffect(() => {
    const handleOpen = (event: Event) => {
      const customEvent = event as CustomEvent<PassInfinityOpenDetail>;
      if (customEvent.detail?.path) {
        setPendingOpen(customEvent.detail);
      }
    };

    window.addEventListener("passinfinity-open", handleOpen);
    return () => window.removeEventListener("passinfinity-open", handleOpen);
  }, []);

  useEffect(() => {
    if (!isLoading && pendingOpen?.path) {
      setDialogOpen(true);
    }
  }, [isLoading, pendingOpen]);

  return (
    <>
      <MessageList>
        {messages.map((msg) => (
          <MessageItem
            key={msg.message_id}
            message={msg}
            onRetry={retryMessage}
            onFeedback={toggleFeedback}
          />
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

      <Dialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setPendingOpen(null);
        }}
      >
        <DialogContent className="w-[92vw] max-w-md rounded-2xl border-slate-200 p-6">
          <DialogTitle>{pendingOpen?.title || "打开 PassInfinity"}</DialogTitle>
          <DialogDescription className="mt-2 leading-6 text-slate-600">
            {pendingOpen?.description || "Agent 准备带你进入 PassInfinity 页面。"}
          </DialogDescription>

          {pendingOpen?.instructions && pendingOpen.instructions.length > 0 && (
            <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
              {pendingOpen.instructions.map((item, index) => (
                <p key={`${item}-${index}`}>
                  {index + 1}. {item}
                </p>
              ))}
            </div>
          )}

          <div className="mt-6 flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => {
                setDialogOpen(false);
                setPendingOpen(null);
              }}
            >
              暂不跳转
            </Button>
            <Button
              className="bg-slate-900 text-white hover:bg-slate-800"
              onClick={() => {
                const path = pendingOpen?.path;
                setDialogOpen(false);
                setPendingOpen(null);
                if (path) {
                  const returnTo = `/chat/${sessionId}`;
                  const separator = path.includes("?") ? "&" : "?";
                  router.push(`${path}${separator}returnTo=${encodeURIComponent(returnTo)}`);
                }
              }}
            >
              去看看
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
