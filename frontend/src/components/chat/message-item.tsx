"use client";

import { type ChatMessage } from "@/hooks/use-chat";
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
          "max-w-[80%] rounded-2xl px-4 py-2.5",
          isHuman
            ? "bg-slate-900 text-white"
            : "bg-transparent",
        )}
      >
        {isHuman ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : (
          <div className="text-sm text-slate-800">
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
      <div className="max-w-[80%] rounded-2xl px-4 py-2.5">
        <div className="text-sm text-slate-800">
          <MarkdownText>{content}</MarkdownText>
        </div>
      </div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex h-8 items-center gap-1 rounded-2xl bg-slate-100 px-4 py-2">
        <div className="h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_infinite] rounded-full bg-slate-400" />
        <div className="h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_0.5s_infinite] rounded-full bg-slate-400" />
        <div className="h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_1s_infinite] rounded-full bg-slate-400" />
      </div>
    </div>
  );
}
