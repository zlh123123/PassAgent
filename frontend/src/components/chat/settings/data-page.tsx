"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { apiDelete, apiGet } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Download } from "lucide-react";

type ConvOption = "all" | "current";
type ExportFormat = "json" | "csv" | "md";
type MemoryType = "PREFERENCE" | "FACT" | "CONSTRAINT";

interface ExportMessage {
  message_id: string;
  content: string;
  message_type: string;
  created_at: string;
}

interface ExportSession {
  session_id: string;
  title: string;
  created_at: string;
  messages: ExportMessage[];
}

interface ExportMemorySection {
  memory_type: MemoryType;
  label: string;
  items: string[];
}

interface ExportMemoryProfile {
  content_md: string;
  sections: ExportMemorySection[];
  created_at: string;
  updated_at: string;
  last_used_at?: string | null;
}

interface ExportResults {
  exported_at: string;
  sessions?: ExportSession[];
  memoryProfile?: ExportMemoryProfile;
  settings?: Record<string, unknown>;
}

function escapeCsvField(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function convertToCsv(data: ExportResults): string {
  const lines: string[] = [];

  if (data.sessions?.length) {
    lines.push("session_id,session_title,message_id,message_type,content,created_at");
    for (const session of data.sessions) {
      for (const message of session.messages) {
        lines.push(
          [session.session_id, session.title, message.message_id, message.message_type, message.content, message.created_at]
            .map((value) => escapeCsvField(String(value ?? "")))
            .join(","),
        );
      }
    }
  }

  if (data.memoryProfile) {
    lines.push("");
    lines.push("memory_type,section_label,content,profile_created_at,profile_updated_at,last_used_at");
    for (const section of data.memoryProfile.sections) {
      for (const item of section.items) {
        lines.push(
          [
            section.memory_type,
            section.label,
            item,
            data.memoryProfile.created_at,
            data.memoryProfile.updated_at,
            data.memoryProfile.last_used_at ?? "",
          ]
            .map((value) => escapeCsvField(String(value ?? "")))
            .join(","),
        );
      }
    }
  }

  return lines.join("\n");
}

function convertToMarkdown(data: ExportResults): string {
  const parts: string[] = [`# PassAgent 数据导出\n\n导出时间：${data.exported_at}\n`];

  if (data.sessions?.length) {
    parts.push("## 对话记录\n");
    for (const session of data.sessions) {
      parts.push(`### ${session.title || "未命名会话"}\n`);
      parts.push(`- 会话 ID：${session.session_id}`);
      parts.push(`- 创建时间：${session.created_at}\n`);
      for (const message of session.messages) {
        const role = message.message_type === "user" ? "用户" : "助手";
        parts.push(`**${role}**（${message.created_at}）\n`);
        parts.push(`${message.content}\n`);
      }
      parts.push("---\n");
    }
  }

  if (data.memoryProfile) {
    parts.push("## 用户记忆\n");
    parts.push(`- 创建时间：${data.memoryProfile.created_at}`);
    parts.push(`- 最近更新：${data.memoryProfile.updated_at}`);
    if (data.memoryProfile.last_used_at) {
      parts.push(`- 最近使用：${data.memoryProfile.last_used_at}`);
    }
    parts.push("");
    parts.push(data.memoryProfile.content_md.trim());
    parts.push("");
  }

  if (data.settings) {
    parts.push("## 用户设置\n");
    for (const [key, value] of Object.entries(data.settings)) {
      parts.push(`- **${key}**：${value}`);
    }
    parts.push("");
  }

  return parts.join("\n");
}

export function DataPage() {
  const pathname = usePathname();
  const match = pathname.match(/^\/chat\/(.+)$/);
  const currentSessionId = match ? match[1] : null;

  const [convOption, setConvOption] = useState<ConvOption>("all");
  const [includeMemories, setIncludeMemories] = useState(true);
  const [includeSettings, setIncludeSettings] = useState(false);
  const [format, setFormat] = useState<ExportFormat>("json");
  const [exporting, setExporting] = useState(false);

  const [clearingConversations, setClearingConversations] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      const results: ExportResults = {
        exported_at: new Date().toISOString(),
      };
      const promises: Promise<void>[] = [];

      const convUrl =
        convOption === "current" && currentSessionId
          ? `/api/export/conversations?session_id=${currentSessionId}&format=${format}`
          : `/api/export/conversations?format=${format}`;
      promises.push(
        apiGet<{ conversations: ExportSession[] }>(convUrl).then((data) => {
          results.sessions = data.conversations;
        }),
      );

      if (includeMemories) {
        promises.push(
          apiGet<{ memory_profile: ExportMemoryProfile }>("/api/export/memories").then((data) => {
            results.memoryProfile = data.memory_profile;
          }),
        );
      }

      if (includeSettings && format !== "csv") {
        promises.push(
          apiGet<{ settings: Record<string, unknown> }>("/api/export/settings").then((data) => {
            results.settings = data.settings;
          }),
        );
      }

      await Promise.all(promises);

      const ext = format === "md" ? "md" : format;
      const mimeMap: Record<string, string> = {
        json: "application/json",
        csv: "text/csv",
        md: "text/markdown",
      };

      let content: string;
      if (format === "csv") {
        content = convertToCsv(results);
      } else if (format === "md") {
        content = convertToMarkdown(results);
      } else {
        content = JSON.stringify(results, null, 2);
      }

      const blob = new Blob([content], { type: mimeMap[format] });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `passagent-export-${new Date().toISOString().slice(0, 10)}.${ext}`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch {
      // ignore
    } finally {
      setExporting(false);
    }
  };

  const handleClearConversations = async () => {
    setClearingConversations(true);
    try {
      await apiDelete("/api/sessions");
      window.dispatchEvent(new Event("session-updated"));
      setConfirmClear(false);
    } catch {
      // ignore
    } finally {
      setClearingConversations(false);
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-base font-medium text-slate-900 dark:text-slate-100">数据管理</h3>

      <div>
        <p className="mb-3 text-sm text-slate-600 dark:text-slate-400">数据导出</p>
        <div className="space-y-4 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
          <div className="mb-1 flex items-center gap-2">
            <Download className="h-4 w-4 text-slate-500" />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">导出数据</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">选择要导出的内容：</p>

          <div className="space-y-2">
            <label className="flex cursor-pointer items-center gap-2.5">
              <input
                type="radio"
                name="conv"
                checked={convOption === "all"}
                onChange={() => setConvOption("all")}
                className="accent-slate-900"
              />
              <span className="text-sm text-slate-700 dark:text-slate-300">全部对话记录</span>
            </label>
            <label className={`flex cursor-pointer items-center gap-2.5 ${!currentSessionId ? "opacity-40" : ""}`}>
              <input
                type="radio"
                name="conv"
                checked={convOption === "current"}
                onChange={() => setConvOption("current")}
                disabled={!currentSessionId}
                className="accent-slate-900"
              />
              <span className="text-sm text-slate-700 dark:text-slate-300">
                仅当前会话{!currentSessionId && "（请先打开一个会话）"}
              </span>
            </label>
          </div>

          <div className="space-y-2">
            <label className="flex cursor-pointer items-center gap-2.5">
              <Checkbox checked={includeMemories} onCheckedChange={(value) => setIncludeMemories(!!value)} />
              <span className="text-sm text-slate-700 dark:text-slate-300">用户记忆</span>
            </label>
            <label className={`flex cursor-pointer items-center gap-2.5 ${format === "csv" ? "opacity-40" : ""}`}>
              <Checkbox
                checked={includeSettings}
                onCheckedChange={(value) => setIncludeSettings(!!value)}
                disabled={format === "csv"}
              />
              <span className="text-sm text-slate-700 dark:text-slate-300">用户设置</span>
            </label>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-slate-500 dark:text-slate-400">导出格式：</p>
            <div className="flex gap-2">
              {(["json", "csv", "md"] as ExportFormat[]).map((option) => (
                <Button
                  key={option}
                  size="sm"
                  variant={format === option ? "default" : "outline"}
                  onClick={() => setFormat(option)}
                >
                  {option.toUpperCase()}
                </Button>
              ))}
            </div>
          </div>

          <Button onClick={handleExport} disabled={exporting} className="w-full">
            {exporting ? "导出中..." : "开始导出"}
          </Button>
        </div>
      </div>

      <div>
        <p className="mb-3 text-sm text-slate-600 dark:text-slate-400">清理数据</p>
        <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
          <p className="mb-3 text-xs text-slate-500 dark:text-slate-400">
            这里只会清空对话记录，不会删除你的账户与记忆档案。
          </p>
          {!confirmClear ? (
            <Button
              variant="outline"
              size="sm"
              className="w-full border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950"
              onClick={() => setConfirmClear(true)}
            >
              清空全部对话
            </Button>
          ) : (
            <div className="space-y-2">
              <p className="text-xs text-red-500">确认要清空全部对话记录吗？此操作不可撤销。</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1" onClick={() => setConfirmClear(false)}>
                  取消
                </Button>
                <Button
                  size="sm"
                  className="flex-1 bg-red-600 text-white hover:bg-red-700"
                  onClick={handleClearConversations}
                  disabled={clearingConversations}
                >
                  {clearingConversations ? "清空中..." : "确认清空"}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
