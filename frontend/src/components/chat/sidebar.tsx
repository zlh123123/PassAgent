"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/providers/Auth";
import { type Session } from "@/hooks/use-sessions";
import {
  SquarePen,
  Search,
  Trash2,
  LogOut,
  MessageSquare,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onNewChat: () => void;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onSearch: (query: string) => void;
  loading: boolean;
}

export function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onSearch,
  loading,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearch, setShowSearch] = useState(false);
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    onSearch(value);
  };

  return (
    <div className="flex h-full w-[280px] flex-col border-r border-slate-200 bg-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-3 py-3">
        <h2 className="text-sm font-semibold text-slate-700">对话历史</h2>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setShowSearch(!showSearch)}
          >
            {showSearch ? (
              <X className="h-4 w-4" />
            ) : (
              <Search className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onNewChat}
          >
            <SquarePen className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Search */}
      {showSearch && (
        <div className="border-b border-slate-200 px-3 py-2">
          <Input
            placeholder="搜索对话..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="h-8 text-sm"
          />
        </div>
      )}

      {/* Session List */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {loading ? (
          <div className="space-y-2 px-1">
            {Array.from({ length: 8 }).map((_, i) => (
              <div
                key={i}
                className="h-10 animate-pulse rounded-lg bg-slate-200"
              />
            ))}
          </div>
        ) : sessions.length === 0 ? (
          <p className="px-3 py-8 text-center text-sm text-slate-400">
            暂无对话
          </p>
        ) : (
          <div className="space-y-0.5">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className={cn(
                  "group flex items-center rounded-lg px-3 py-2 text-sm transition-colors cursor-pointer",
                  currentSessionId === session.session_id
                    ? "bg-slate-200 text-slate-900"
                    : "text-slate-600 hover:bg-slate-100",
                )}
                onClick={() => onSelectSession(session.session_id)}
              >
                <MessageSquare className="mr-2 h-4 w-4 shrink-0 text-slate-400" />
                <span className="flex-1 truncate">{session.title}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.session_id);
                  }}
                >
                  <Trash2 className="h-3 w-3 text-slate-400" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* User Menu */}
      <div className="border-t borde-200 px-3 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-xs font-medium text-slate-600">
              {user?.nickname?.charAt(0) || "U"}
            </div>
            <span className="text-sm text-slate-600 truncate max-w-[140px]">
              {user?.nickname || "用户"}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={logout}
          >
            <LogOut className="h-4 w-4 text-slate-400" />
          </Button>
        </div>
      </div>
    </div>
  );
}
