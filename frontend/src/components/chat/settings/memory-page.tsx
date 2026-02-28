"use client";

import { useState, useEffect, useCallback } from "react";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Trash2, Plus } from "lucide-react";

interface Memory {
  memory_id: string;
  content: string;
  memory_type: string;
  source: string;
  created_at: string;
}

export function MemoryPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(false);
  const [newMemory, setNewMemory] = useState("");
  const [newMemoryType, setNewMemoryType] = useState<"PREFERENCE" | "FACT" | "CONSTRAINT">("FACT");

  const [confirmClearAll, setConfirmClearAll] = useState(false);

  const memoryPlaceholders: Record<typeof newMemoryType, string> = {
    FACT: "例如：我的小猫叫哈吉米",
    PREFERENCE: "例如：喜欢8位以上的密码",
    CONSTRAINT: "例如：至少包含两个特殊字符",
  };

  const fetchMemories = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<{ memories: Memory[] }>("/api/memories");
      setMemories(data.memories);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  const handleAdd = async () => {
    if (!newMemory.trim()) return;
    try {
      await apiPost("/api/memories", {
        content: newMemory.trim(),
        memory_type: newMemoryType,
      });
      setNewMemory("");
      fetchMemories();
    } catch {
      // ignore
    }
  };

  const handleDelete = async (memoryId: string) => {
    try {
      await apiDelete(`/api/memories/${memoryId}`);
      setMemories((prev) => prev.filter((m) => m.memory_id !== memoryId));
    } catch {
      // ignore
    }
  };

  const handleClearAll = async () => {
    try {
      await apiDelete("/api/memories");
      setMemories([]);
      setConfirmClearAll(false);
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-base font-medium text-slate-900 dark:text-slate-100">记忆管理</h3>
      <p className="text-xs text-slate-500 dark:text-slate-400">
        记忆帮助 Agent 更好地了解你的偏好，生成更个性化的建议。
      </p>

      {/* Add memory */}
      <div className="flex gap-2">
        <select
          value={newMemoryType}
          onChange={(e) => setNewMemoryType(e.target.value as typeof newMemoryType)}
          className="rounded-md border border-slate-200 dark:border-slate-700 px-2 py-1.5 text-sm bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300"
        >
          <option value="FACT">事实</option>
          <option value="PREFERENCE">偏好</option>
          <option value="CONSTRAINT">约束</option>
        </select>
        <Input
          value={newMemory}
          onChange={(e) => setNewMemory(e.target.value)}
          placeholder={memoryPlaceholders[newMemoryType]}
          className="flex-1"
          onKeyDown={(e) => e.key === "Enter" && handleAdd()}
        />
        <Button size="icon" variant="outline" onClick={handleAdd} disabled={!newMemory.trim()}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {/* Memory list */}
      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 animate-pulse rounded-lg bg-slate-100 dark:bg-slate-800" />
          ))}
        </div>
      ) : memories.length === 0 ? (
        <p className="text-center text-sm text-slate-400 dark:text-slate-500 py-6">暂无记忆</p>
      ) : (
        <div className="space-y-2">
          {memories.map((memory) => (
            <div
              key={memory.memory_id}
              className="group flex items-start gap-2 rounded-lg border border-slate-200 dark:border-slate-700 p-3"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-700 dark:text-slate-300">{memory.content}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                    {memory.memory_type === "PREFERENCE"
                      ? "偏好"
                      : memory.memory_type === "CONSTRAINT"
                        ? "约束"
                        : "事实"}
                  </span>
                  <span className="text-xs text-slate-400">
                    {memory.source === "auto" ? "自动提取" : "手动添加"}
                  </span>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 shrink-0 opacity-0 group-hover:opacity-100"
                onClick={() => handleDelete(memory.memory_id)}
              >
                <Trash2 className="h-3.5 w-3.5 text-slate-400" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Clear all */}
      {memories.length > 0 && (
        <div className="border-t border-dashed border-slate-200 dark:border-slate-700 pt-4">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
            清除后所有记忆将永久丢失，Agent 将无法参考你的偏好。
          </p>
          {!confirmClearAll ? (
            <Button
              variant="outline"
              size="sm"
              className="w-full text-red-600 border-red-200 hover:bg-red-50 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-950"
              onClick={() => setConfirmClearAll(true)}
            >
              清除全部记忆
            </Button>
          ) : (
            <div className="space-y-2">
              <p className="text-xs text-red-500">此操作不可撤销，确定要清除全部记忆吗？</p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => setConfirmClearAll(false)}
                >
                  取消
                </Button>
                <Button
                  size="sm"
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                  onClick={handleClearAll}
                >
                  确认清除
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
