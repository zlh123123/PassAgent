"use client";

import { useState } from "react";
import { type ChatMessage } from "@/hooks/use-chat";
import { useAuth } from "@/providers/Auth";
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

const fontSizeMap: Record<string, string> = {
  S: "13px",
  M: "15px",
  L: "17px",
  XL: "19px",
};

function getBubbleClasses(style: string, isHuman: boolean) {
  if (style === "minimal") {
    return isHuman
      ? "max-w-[80%] border-b border-slate-300 dark:border-slate-700 px-4 py-2.5 text-slate-900 dark:text-slate-100"
      : "w-full px-4 py-2.5";
  }
  if (style === "square") {
    return isHuman
      ? "max-w-[80%] rounded-[6px] bg-slate-900 text-white px-4 py-2.5"
      : "w-full bg-transparent px-4 py-2.5";
  }
  // rounded (default)
  return isHuman
    ? "max-w-[80%] rounded-2xl bg-slate-900 text-white px-4 py-2.5"
    : "w-full bg-transparent rounded-2xl px-4 py-2.5";
}

interface MessageItemProps {
  message: ChatMessage;
  onRetry?: (messageId: string) => void;
  onFeedback?: (messageId: string, type: "like" | "dislike") => void;
}

export function MessageItem({ message, onRetry, onFeedback }: MessageItemProps) {
  const { user } = useAuth();
  const isHuman = message.message_type === "human";
  const [copied, setCopied] = useState(false);

  const fontSize = fontSizeMap[user?.font_size || "M"] || "15px";
  const bubbleStyle = user?.bubble_style || "rounded";

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
      <div className={cn(getBubbleClasses(bubbleStyle, isHuman))}>
        {!isHuman && message.agent_steps && message.agent_steps.length > 0 && (
          <AgentSteps steps={message.agent_steps} isStreaming={false} />
        )}
        {isHuman ? (
          <p className="whitespace-pre-wrap" style={{ fontSize }}>{message.content}</p>
        ) : (
          <div className="text-slate-800 dark:text-slate-200" style={{ fontSize }}>
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
  const { user } = useAuth();
  if (!content) return null;

  const fontSize = fontSizeMap[user?.font_size || "M"] || "15px";

  return (
    <div className="flex justify-start">
      <div className="w-full rounded-2xl px-4 py-2.5">
        <div className="text-slate-800 dark:text-slate-200" style={{ fontSize }}>
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
