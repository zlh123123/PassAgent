"use client";

import { useState } from "react";
import { useAuth } from "@/providers/Auth";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { AccountPage } from "@/components/chat/settings/account-page";
import { AppearancePage } from "@/components/chat/settings/appearance-page";
import { GenerationPage } from "@/components/chat/settings/generation-page";
import { MemoryPage } from "@/components/chat/settings/memory-page";
import { DataPage } from "@/components/chat/settings/data-page";
import { AboutPage } from "@/components/chat/settings/about-page";
import {
  User,
  Palette,
  KeyRound,
  Brain,
  HardDrive,
  Info,
  LogOut,
} from "lucide-react";

type Page = "account" | "appearance" | "generation" | "memory" | "data" | "about";

const navItems: { key: Page; label: string; icon: React.ReactNode }[] = [
  { key: "account", label: "账户", icon: <User className="h-4 w-4" /> },
  { key: "appearance", label: "外观", icon: <Palette className="h-4 w-4" /> },
  { key: "generation", label: "口令生成", icon: <KeyRound className="h-4 w-4" /> },
  { key: "memory", label: "记忆", icon: <Brain className="h-4 w-4" /> },
  { key: "data", label: "导出", icon: <HardDrive className="h-4 w-4" /> },
  { key: "about", label: "关于", icon: <Info className="h-4 w-4" /> },
];

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  const { logout } = useAuth();
  const [page, setPage] = useState<Page>("account");

  const handleLogout = () => {
    onOpenChange(false);
    logout();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl w-[90vw] max-h-[85vh] p-0 gap-0 overflow-hidden">
        <DialogTitle className="sr-only">设置</DialogTitle>
        <div className="flex h-[70vh]">
          {/* Left nav */}
          <nav className="w-[180px] shrink-0 border-r border-slate-200 dark:border-slate-800 flex flex-col bg-slate-50/50 dark:bg-slate-900/50">
            <div className="px-4 py-4">
              <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">设置</h2>
            </div>
            <div className="flex-1 px-2 space-y-0.5">
              {navItems.map((item) => (
                <button
                  key={item.key}
                  onClick={() => setPage(item.key)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                    page === item.key
                      ? "bg-slate-200 dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-medium"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60"
                  }`}
                >
                  {item.icon}
                  {item.label}
                </button>
              ))}
            </div>
            <div className="px-2 pb-4">
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/50 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                退出登录
              </button>
            </div>
          </nav>

          {/* Right content */}
          <div className="flex-1 overflow-y-auto p-6">
            {page === "account" && <AccountPage />}
            {page === "appearance" && <AppearancePage />}
            {page === "generation" && <GenerationPage />}
            {page === "memory" && <MemoryPage />}
            {page === "data" && <DataPage />}
            {page === "about" && <AboutPage />}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
