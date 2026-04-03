"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/providers/Auth";
import { apiPut } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { MemoryPage } from "@/components/chat/settings/memory-page";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Brain, LogOut, Palette, User } from "lucide-react";

interface SettingsPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type Tab = "profile" | "appearance" | "memory";

export function SettingsPanel({ open, onOpenChange }: SettingsPanelProps) {
  const { user, logout, setAuth, token } = useAuth();
  const [tab, setTab] = useState<Tab>("profile");
  const [nickname, setNickname] = useState("");
  const [saving, setSaving] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    if (open && user) {
      setNickname(user.nickname || "");
      setIsDark(user.theme === "dark");
    }
  }, [open, user]);

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
    const nextTheme = isDark ? "light" : "dark";
    setIsDark(!isDark);
    document.documentElement.classList.toggle("dark", nextTheme === "dark");
    try {
      await apiPut("/api/user/profile", { theme: nextTheme });
      if (user && token) {
        setAuth(token, { ...user, theme: nextTheme });
      }
    } catch {
      setIsDark(isDark);
      document.documentElement.classList.toggle("dark", isDark);
    }
  };

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: "profile", label: "个人资料", icon: <User className="h-4 w-4" /> },
    { key: "appearance", label: "外观", icon: <Palette className="h-4 w-4" /> },
    { key: "memory", label: "记忆管理", icon: <Brain className="h-4 w-4" /> },
  ];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-[400px] flex-col p-0 sm:max-w-[400px]">
        <SheetHeader className="px-6 pb-2 pt-6">
          <SheetTitle>设置</SheetTitle>
          <SheetDescription>管理你的账户和偏好</SheetDescription>
        </SheetHeader>

        <div className="flex gap-1 border-b border-slate-200 px-6 pb-3 dark:border-slate-800">
          {tabs.map((item) => (
            <button
              key={item.key}
              onClick={() => setTab(item.key)}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors ${
                tab === item.key
                  ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              }`}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4">
          {tab === "profile" && (
            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">昵称</label>
                <Input value={nickname} onChange={(e) => setNickname(e.target.value)} placeholder="输入昵称" />
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
                  <p className="mt-0.5 text-xs text-slate-500">切换深色/浅色主题</p>
                </div>
                <Switch checked={isDark} onCheckedChange={handleToggleTheme} />
              </div>
            </div>
          )}

          {tab === "memory" && <MemoryPage />}
        </div>

        <div className="border-t border-slate-200 px-6 py-4 dark:border-slate-800">
          <Button
            variant="outline"
            className="w-full border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950 dark:hover:text-red-300"
            onClick={() => {
              onOpenChange(false);
              logout();
            }}
          >
            <LogOut className="mr-2 h-4 w-4" />
            退出登录
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
