"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { apiDelete, apiGet, apiPost } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Trash2 } from "lucide-react";

type MemoryType = "PREFERENCE" | "FACT" | "CONSTRAINT";

interface MemorySection {
  memory_type: MemoryType;
  label: string;
  items: string[];
}

interface MemoryProfile {
  content_md: string;
  sections: MemorySection[];
  created_at: string;
  updated_at: string;
  last_used_at?: string | null;
}

interface MemoryListItem {
  content: string;
  memory_type: MemoryType;
}

const memoryTypeMeta: Record<
  MemoryType,
  {
    label: string;
  }
> = {
  FACT: {
    label: "事实",
  },
  PREFERENCE: {
    label: "偏好",
  },
  CONSTRAINT: {
    label: "约束",
  },
};

export function MemoryPage() {
  const [profile, setProfile] = useState<MemoryProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [newMemory, setNewMemory] = useState("");
  const [newMemoryType, setNewMemoryType] = useState<MemoryType>("FACT");
  const [confirmClearAll, setConfirmClearAll] = useState(false);

  const memoryPlaceholders: Record<MemoryType, string> = {
    FACT: "例如：我的小猫叫哈吉米",
    PREFERENCE: "例如：偏好 14-16 位密码",
    CONSTRAINT: "例如：工作密码必须 90 天轮换",
  };

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<MemoryProfile>("/api/memories");
      setProfile(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const memories = useMemo<MemoryListItem[]>(
    () =>
      profile?.sections.flatMap((section) =>
        section.items.map((item) => ({
          content: item,
          memory_type: section.memory_type,
        })),
      ) ?? [],
    [profile],
  );

  const handleAdd = async () => {
    if (!newMemory.trim()) return;
    try {
      await apiPost("/api/memories/items", {
        content: newMemory.trim(),
        memory_type: newMemoryType,
      });
      setNewMemory("");
      await fetchProfile();
    } catch {
      // ignore
    }
  };

  const handleDelete = async (memoryType: MemoryType, content: string) => {
    try {
      await apiDelete(
        `/api/memories/items?memory_type=${encodeURIComponent(memoryType)}&content=${encodeURIComponent(content)}`,
      );
      await fetchProfile();
    } catch {
      // ignore
    }
  };

  const handleClearAll = async () => {
    try {
      await apiDelete("/api/memories");
      setConfirmClearAll(false);
      await fetchProfile();
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

      <div className="flex gap-2">
        <select
          value={newMemoryType}
          onChange={(e) => setNewMemoryType(e.target.value as MemoryType)}
          className="rounded-md border border-slate-200 bg-white px-2 py-1.5 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
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

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="h-12 animate-pulse rounded-lg bg-slate-100 dark:bg-slate-800" />
          ))}
        </div>
      ) : !profile ? (
        <p className="py-6 text-center text-sm text-slate-400 dark:text-slate-500">记忆加载失败</p>
      ) : memories.length === 0 ? (
        <p className="py-6 text-center text-sm text-slate-400 dark:text-slate-500">暂无记忆</p>
      ) : (
        <div className="space-y-2">
          {memories.map((memory) => (
            <div
              key={`${memory.memory_type}-${memory.content}`}
              className="group flex items-center gap-3 rounded-2xl border border-slate-200/80 bg-white/80 p-3 shadow-[0_1px_2px_rgba(15,23,42,0.04)] backdrop-blur-sm dark:border-slate-700/80 dark:bg-slate-900/60"
            >
              <span className="shrink-0 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium tracking-[0.01em] text-slate-500 dark:border-slate-700 dark:bg-slate-800/80 dark:text-slate-400">
                {memoryTypeMeta[memory.memory_type].label}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm leading-6 text-slate-700 dark:text-slate-300">{memory.content}</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 shrink-0 rounded-full opacity-0 transition-opacity group-hover:opacity-100"
                onClick={() => handleDelete(memory.memory_type, memory.content)}
              >
                <Trash2 className="h-3.5 w-3.5 text-slate-400" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {memories.length > 0 && (
        <div className="border-t border-dashed border-slate-200 pt-4 dark:border-slate-700">
          <p className="mb-3 text-xs text-slate-500 dark:text-slate-400">
            清除后所有记忆将永久丢失，Agent 将无法参考你的偏好。
          </p>
          {!confirmClearAll ? (
            <Button
              variant="outline"
              size="sm"
              className="w-full border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950"
              onClick={() => setConfirmClearAll(true)}
            >
              清除全部记忆
            </Button>
          ) : (
            <div className="space-y-2">
              <p className="text-xs text-red-500">此操作不可撤销，确定要清除全部记忆吗？</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1" onClick={() => setConfirmClearAll(false)}>
                  取消
                </Button>
                <Button size="sm" className="flex-1 bg-red-600 text-white hover:bg-red-700" onClick={handleClearAll}>
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
