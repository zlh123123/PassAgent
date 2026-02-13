"use client";

import { type ChatMessage } from "@/hooks/use-chat";
import { AgentSteps } from "./agent-steps";
import { MarkdownText } from "./markdown-text";
import { cn } from "@/lib/utils";

interface MessageItemProps {
  message: ChatMessage;
}

export function MessageItem({ message }: MessageItemProps) {
  const isHuman = message.message_type === "human";

  return (
    <div className={cn("flex", isHuman ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "rounded-2xl px-4 py-2.5",
          isHuman
            ? "max-w-[80%] bg-slate-900 text-white"
            : "w-full bg-transparent",
        )}
      >
        {!isHuman && message.agent_steps && message.agent_steps.length > 0 && (
          <AgentSteps steps={message.agent_steps} isStreaming={false} />
        )}
        {isHuman ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : (
          <div className="text-sm text-slate-800 dark:text-slate-200">
            <MarkdownText>{message.content}</MarkdownText>
          </div>
        )}
      </div>
    </div>
  );
}

export function StreamingMessage({ content }: { content: string }) {
  if (!content) return null;

  return (
    <div className="flex justify-start">
      <div className="w-full rounded-2xl px-4 py-2.5">
        <div className="text-sm text-slate-800 dark:text-slate-200">
          <MarkdownText>{content}</MarkdownText>
        </div>
      </div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex h-8 items-center gap-1 rounded-2xl bg-slate-100 dark:bg-slate-800 px-4 py-2">
        <div className="h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_infinite] rounded-full bg-slate-400 dark:bg-slate-500" />
        <div className="h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_0.5s_infinite] rounded-full bg-slate-400 dark:bg-slate-500" />
        <div className="h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_1s_infinite] rounded-full bg-slate-400 dark:bg-slate-500" />
      </div>
    </div>
  );
}
