"use client";

import { useState, FormEvent, useRef } from "react";
import { Button } from "@/components/ui/button";
import { SendHorizonal, Paperclip, LoaderCircle, X, FileImage, FileAudio } from "lucide-react";
import { API_BASE } from "@/lib/api";

interface UploadedFile {
  file_id: string;
  filename: string;
  file_type: string;
  file_size: number;
}

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
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend(input.trim(), files.map((f) => f.file_id));
    setInput("");
    setFiles([]);
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

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files;
    if (!selected || selected.length === 0) return;

    setUploading(true);
    try {
      for (const file of Array.from(selected)) {
        const formData = new FormData();
        formData.append("file", file);

        const token = localStorage.getItem("token");
        const res = await fetch(`${API_BASE}/api/upload`, {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData,
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: "上传失败" }));
          console.error("Upload failed:", err.detail);
          continue;
        }

        const data: UploadedFile = await res.json();
        setFiles((prev) => [...prev, data]);
      }
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const removeFile = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.file_id !== fileId));
  };

  const isImage = (type: string) => type.startsWith("image/");

  return (
    <div className="bg-white dark:bg-slate-950 px-4 py-3">
      <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
        {/* File previews */}
        {files.length > 0 && (
          <div className="flex gap-2 mb-2 flex-wrap">
            {files.map((file) => (
              <div
                key={file.file_id}
                className="flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2.5 py-1.5 text-xs text-slate-600 dark:text-slate-400"
              >
                {isImage(file.file_type) ? (
                  <FileImage className="h-3.5 w-3.5 text-slate-400" />
                ) : (
                  <FileAudio className="h-3.5 w-3.5 text-slate-400" />
                )}
                <span className="max-w-[120px] truncate">{file.filename}</span>
                <button
                  type="button"
                  onClick={() => removeFile(file.file_id)}
                  className="ml-0.5 rounded p-0.5 hover:bg-slate-200 dark:hover:bg-slate-700"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex items-end gap-2 rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 p-2 shadow-sm transition-colors focus-within:border-slate-300 dark:focus-within:border-slate-600 focus-within:bg-white dark:focus-within:bg-slate-800">
          {/* File upload button */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp,audio/wav,audio/mpeg,audio/flac"
            multiple
            className="hidden"
            onChange={handleFileSelect}
          />
          <Button
            type="button"
            size="sm"
            variant="ghost"
            className="shrink-0 rounded-xl h-8 w-8 p-0"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading || isLoading}
          >
            {uploading ? (
              <LoaderCircle className="h-4 w-4 animate-spin text-slate-400" />
            ) : (
              <Paperclip className="h-4 w-4 text-slate-400" />
            )}
          </Button>

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 200) + "px";
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={1}
            className="flex-1 resize-none border-none bg-transparent px-2 py-1.5 text-sm text-slate-900 dark:text-slate-100 outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
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
