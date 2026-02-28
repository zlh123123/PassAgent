"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { apiGet, apiDelete } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Download } from "lucide-react";

type ConvOption = "all" | "current";
type ExportFormat = "json" | "csv" | "md";

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
      const results: Record<string, unknown> = {
        exported_at: new Date().toISOString(),
      };
      const promises: Promise<void>[] = [];

      // 对话
      const convUrl =
        convOption === "current" && currentSessionId
          ? `/api/export/conversations?session_id=${currentSessionId}&format=${format}`
          : `/api/export/conversations?format=${format}`;
      promises.push(
        apiGet<{ conversations: unknown }>(convUrl).then((d) => {
          results.sessions = d.conversations;
        }),
      );

      if (includeMemories) {
        promises.push(
          apiGet<{ memories: unknown }>("/api/export/memories").then((d) => {
            results.memories = d.memories;
          }),
        );
      }
      if (includeSettings && format !== "csv") {
        promises.push(
          apiGet<{ settings: unknown }>("/api/export/settings").then((d) => {
            results.settings = d.settings;
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
      const blob = new Blob([JSON.stringify(results, null, 2)], {
        type: mimeMap[format],
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `passagent-export-${new Date().toISOString().slice(0, 10)}.${ext}`;
      a.click();
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

      {/* 导出数据 */}
      <div>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">数据导出</p>
        <div className="rounded-lg border border-slate-200 dark:border-slate-700 p-4 space-y-4">
          <div className="flex items-center gap-2 mb-1">
            <Download className="h-4 w-4 text-slate-500" />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">导出数据</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">选择要导出的内容：</p>

          {/* 对话选项 - 互斥单选 */}
          <div className="space-y-2">
            <label className="flex items-center gap-2.5 cursor-pointer">
              <input
                type="radio"
                name="conv"
                checked={convOption === "all"}
                onChange={() => setConvOption("all")}
                className="accent-slate-900"
              />
              <span className="text-sm text-slate-700 dark:text-slate-300">全部对话记录</span>
            </label>
            <label className={`flex items-center gap-2.5 cursor-pointer ${!currentSessionId ? "opacity-40" : ""}`}>
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

          {/* 其他选项 - 独立勾选 */}
          <div className="space-y-2">
            <label className="flex items-center gap-2.5 cursor-pointer">
              <Checkbox checked={includeMemories} onCheckedChange={(v) => setIncludeMemories(!!v)} />
              <span className="text-sm text-slate-700 dark:text-slate-300">用户记忆</span>
            </label>
            <label className={`flex items-center gap-2.5 cursor-pointer ${format === "csv" ? "opacity-40" : ""}`}>
              <Checkbox
                checked={includeSettings}
                onCheckedChange={(v) => setIncludeSettings(!!v)}
                disabled={format === "csv"}
              />
              <span className="text-sm text-slate-700 dark:text-slate-300">
                用户设置{format === "csv" && "（CSV 格式不支持）"}
              </span>
            </label>
          </div>

          {/* 格式选择 */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-600 dark:text-slate-400">导出格式：</span>
            <select
              value={format}
              onChange={(e) => {
                const f = e.target.value as ExportFormat;
                setFormat(f);
                if (f === "csv") setIncludeSettings(false);
              }}
              className="rounded-md border border-slate-200 dark:border-slate-700 px-2.5 py-1.5 text-sm bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300"
            >
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="md">Markdown</option>
            </select>
          </div>

          <Button
            onClick={handleExport}
            disabled={exporting}
            className="w-full"
            size="sm"
          >
            {exporting ? "导出中..." : "导出"}
          </Button>
        </div>
      </div>

      {/* 清除对话 */}
      <div className="border-t border-dashed border-slate-200 dark:border-slate-700 pt-5">
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          删除全部会话及消息记录，不可恢复。
        </p>
        {!confirmClear ? (
          <Button
            variant="outline"
            className="w-full text-red-600 border-red-200 hover:bg-red-50 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-950"
            size="sm"
            onClick={() => setConfirmClear(true)}
          >
            清除所有对话
          </Button>
        ) : (
          <div className="space-y-2">
            <p className="text-xs text-red-500">此操作不可撤销，确定要清除所有对话吗？</p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() => setConfirmClear(false)}
              >
                取消
              </Button>
              <Button
                size="sm"
                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                onClick={handleClearConversations}
                disabled={clearingConversations}
              >
                {clearingConversations ? "清除中..." : "确认清除"}
              </Button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
