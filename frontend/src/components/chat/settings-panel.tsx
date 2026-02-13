"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/providers/Auth";
import { apiGet, apiPut, apiPost, apiDelete } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Trash2, Plus, LogOut, User, Palette, Brain } from "lucide-react";

interface Memory {
  memory_id: string;
  content: string;
  memory_type: string;
  source: string;
  created_at: string;
}

interface Profile {
  user_id: string;
  email: string;
  nickname: string;
  theme: string;
}

interface SettingsPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type Tab = "profile" | "appearance" | "memory";

export function SettingsPanel({ open, onOpenChange }: SettingsPanelProps) {
  const { user, logout, setAuth, token } = useAuth();
  const [tab, setTab] = useState<Tab>("profile");

  // Profile state
  const [nickname, setNickname] = useState("");
  const [saving, setSaving] = useState(false);

  // Theme state
  const [isDark, setIsDark] = useState(false);

  // Memory state
  const [memories, setMemories] = useState<Memory[]>([]);
  const [memoriesLoading, setMemoriesLoading] = useState(false);
  const [newMemory, setNewMemory] = useState("");
  const [newMemoryType, setNewMemoryType] = useState<"PREFERENCE" | "FACT" | "CONSTRAINT">("FACT");

  const memoryPlaceholders: Record<typeof newMemoryType, string> = {
    FACT: "例如：我的小猫叫哈吉米",
    PREFERENCE: "例如：喜欢8位以上的密码",
    CONSTRAINT: "例如：至少包含两个特殊字符",
  };

  useEffect(() => {
    if (open && user) {
      setNickname(user.nickname || "");
      setIsDark(user.theme === "dark");
    }
  }, [open, user]);

  const fetchMemories = useCallback(async () => {
    setMemoriesLoading(true);
    try {
      const data = await apiGet<{ memories: Memory[] }>("/api/memories");
      setMemories(data.memories);
    } catch {
      // ignore
    } finally {
      setMemoriesLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open && tab === "memory") {
      fetchMemories();
    }
  }, [open, tab, fetchMemories]);

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      await apiPut("/api/user/profile", { nickname });
      if (user && token) {
        setAuth(token, { ...user, nickname });
      }
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  };

  const handleToggleTheme = async () => {
    const newTheme = isDark ? "light" : "dark";
    setIsDark(!isDark);
    // Apply dark class to html element
    document.documentElement.classList.toggle("dark", newTheme === "dark");
    try {
      await apiPut("/api/user/profile", { theme: newTheme });
      if (user && token) {
        setAuth(token, { ...user, theme: newTheme });
      }
    } catch {
      setIsDark(isDark);
      document.documentElement.classList.toggle("dark", isDark);
    }
  };

  const handleAddMemory = async () => {
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

  const handleDeleteMemory = async (memoryId: string) => {
    try {
      await apiDelete(`/api/memories/${memoryId}`);
      setMemories((prev) => prev.filter((m) => m.memory_id !== memoryId));
    } catch {
      // ignore
    }
  };

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: "profile", label: "个人资料", icon: <User className="h-4 w-4" /> },
    { key: "appearance", label: "外观", icon: <Palette className="h-4 w-4" /> },
    { key: "memory", label: "记忆管理", icon: <Brain className="h-4 w-4" /> },
  ];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-[400px] sm:max-w-[400px] p-0 flex flex-col">
        <SheetHeader className="px-6 pt-6 pb-2">
          <SheetTitle>设置</SheetTitle>
          <SheetDescription>管理你的账户和偏好</SheetDescription>
        </SheetHeader>

        {/* Tabs */}
        <div className="flex gap-1 px-6 pb-3 border-b border-slate-200 dark:border-slate-800">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
                tab === t.key
                  ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {tab === "profile" && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 mb-1.5 block">
                  昵称
                </label>
                <Input
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  placeholder="输入昵称"
                />
              </div>
              <Button
                onClick={handleSaveProfile}
                disabled={saving || nickname === (user?.nickname || "")}
                className="w-full bg-slate-900 hover:bg-slate-800"
              >
                {saving ? "保存中..." : "保存"}
              </Button>
            </div>
          )}

          {tab === "appearance" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border border-slate-200 p-4">
                <div>
                  <p className="text-sm font-medium text-slate-700">深色模式</p>
                  <p className="text-xs text-slate-500 mt-0.5">切换深色/浅色主题</p>
                </div>
                <Switch checked={isDark} onCheckedChange={handleToggleTheme} />
              </div>
            </div>
          )}

          {tab === "memory" && (
            <div className="space-y-4">
              <p className="text-xs text-slate-500">
                记忆帮助 Agent 更好地了解你的偏好，生成更个性化的建议。
              </p>

              {/* Add memory */}
              <div className="space-y-2">
                <div className="flex gap-2">
                  <select
                    value={newMemoryType}
                    onChange={(e) => setNewMemoryType(e.target.value as typeof newMemoryType)}
                    className="rounded-md border border-slate-200 px-2 py-1.5 text-sm bg-white text-slate-700"
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
                    onKeyDown={(e) => e.key === "Enter" && handleAddMemory()}
                  />
                  <Button
                    size="icon"
                    variant="outline"
                    onClick={handleAddMemory}
                    disabled={!newMemory.trim()}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Memory list */}
              {memoriesLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="h-12 animate-pulse rounded-lg bg-slate-100" />
                  ))}
                </div>
              ) : memories.length === 0 ? (
                <p className="text-center text-sm text-slate-400 py-6">暂无记忆</p>
              ) : (
                <div className="space-y-2">
                  {memories.map((memory) => (
                    <div
                      key={memory.memory_id}
                      className="group flex items-start gap-2 rounded-lg border border-slate-200 p-3"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-700">{memory.content}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-1.5 py-0.5 rounded bg-slate-100 text-slate-500">
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
                        onClick={() => handleDeleteMemory(memory.memory_id)}
                      >
                        <Trash2 className="h-3.5 w-3.5 text-slate-400" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer - Logout */}
        <div className="border-t border-slate-200 dark:border-slate-800 px-6 py-4">
          <Button
            variant="outline"
            className="w-full text-red-600 dark:text-red-400 border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-950 hover:text-red-700 dark:hover:text-red-300"
            onClick={() => {
              onOpenChange(false);
              logout();
            }}
          >
            <LogOut className="h-4 w-4 mr-2" />
            退出登录
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
