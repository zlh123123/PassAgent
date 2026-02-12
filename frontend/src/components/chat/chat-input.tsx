"use client";

import { useState, FormEvent, useRef } from "react";
import { Button } from "@/components/ui/button";
import { SendHorizonal, Paperclip, LoaderCircle, X } from "lucide-react";

interface ChatInputProps {
  onSend: (content: string, fileIds: string[]) => void;
  isLoading: boolean;
  onStop: () => void;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  isLoading,
  onStop,
  placeholder = "输入你的问题...",
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend(input.trim(), []);
    setInput("");
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      const form = (e.target as HTMLElement).closest("form");
      form?.requestSubmit();
    }
  };

  return (
    <div className="border-t border-slate-200 bg-white px-4 py-3">
      <form
        onSubmit={handleSubmit}
        className="mx-auto max-w-3xl"
      >
        <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 shadow-sm transition-colors focus-within:border-slate-300 focus-within:bg-white">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              // Auto-resize
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 200) + "px";
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={1}
            className="flex-1 resize-none border-none bg-transparent px-2 py-1.5 text-sm outline-none placeholder:text-slate-400"
          />
          {isLoading ? (
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={onStop}
              className="shrink-0 rounded-xl"
            >
              <LoaderCircle className="mr-1 h-4 w-4 animate-spin" />
              停止
            </Button>
          ) : (
            <Button
              type="submit"
              size="sm"
              disabled={!input.trim()}
              className="shrink-0 rounded-xl bg-slate-900 hover:bg-slate-800"
            >
              <SendHorizonal className="h-4 w-4" />
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
