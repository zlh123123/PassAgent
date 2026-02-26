"use client";

import { useState } from "react";
import { type ChatMessage } from "@/hooks/use-chat";
import { AgentSteps } from "./agent-steps";
import { MarkdownText } from "./markdown-text";
import { cn } from "@/lib/utils";
import { TooltipIconButton } from "./tooltip-icon-button";
import {
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  Download,
} from "lucide-react";

interface MessageItemProps {
  message: ChatMessage;
  onRetry?: (messageId: string) => void;
  onFeedback?: (messageId: string, type: "like" | "dislike") => void;
}

export function MessageItem({ message, onRetry, onFeedback }: MessageItemProps) {
  const isHuman = message.message_type === "human";
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleExport = () => {
    const blob = new Blob([message.content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `message-${message.message_id.slice(0, 8)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={cn("group/msg flex", isHuman ? "justify-end" : "justify-start")}>
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
        {!isHuman && (
          <div className="mt-2 flex items-center gap-0.5 opacity-0 transition-opacity group-hover/msg:opacity-100">
            <TooltipIconButton
              tooltip="重试"
              side="top"
              onClick={() => onRetry?.(message.message_id)}
            >
              <RotateCcw className="h-3.5 w-3.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" />
            </TooltipIconButton>
            <TooltipIconButton
              tooltip="点赞"
              side="top"
              onClick={() => onFeedback?.(message.message_id, "like")}
            >
              <ThumbsUp
                className={cn(
                  "h-3.5 w-3.5",
                  message.feedback?.feedback_type === "like"
                    ? "text-blue-500"
                    : "text-slate-400 hover:text-slate-600 dark:hover:text-slate-300",
                )}
              />
            </TooltipIconButton>
            <TooltipIconButton
              tooltip="点踩"
              side="top"
              onClick={() => onFeedback?.(message.message_id, "dislike")}
            >
              <ThumbsDown
                className={cn(
                  "h-3.5 w-3.5",
                  message.feedback?.feedback_type === "dislike"
                    ? "text-red-500"
                    : "text-slate-400 hover:text-slate-600 dark:hover:text-slate-300",
                )}
              />
            </TooltipIconButton>
            <TooltipIconButton
              tooltip={copied ? "已复制" : "复制"}
              side="top"
              onClick={handleCopy}
            >
              {copied ? (
                <Check className="h-3.5 w-3.5 text-green-500" />
              ) : (
                <Copy className="h-3.5 w-3.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" />
              )}
            </TooltipIconButton>
            <TooltipIconButton
              tooltip="导出"
              side="top"
              onClick={handleExport}
            >
              <Download className="h-3.5 w-3.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" />
            </TooltipIconButton>
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
