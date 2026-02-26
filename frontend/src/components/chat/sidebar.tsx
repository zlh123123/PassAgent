"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/providers/Auth";
import { type Session } from "@/hooks/use-sessions";
import {
  SquarePen,
  Search,
  Trash2,
  Settings,
  MessageSquare,
  X,
  PanelLeftClose,
  PanelLeftOpen,
  Pencil,
  Check,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  onNewChat: () => void;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onRenameSession: (sessionId: string, title: string) => void;
  onSearch: (query: string) => void;
  onOpenSettings: () => void;
  loading: boolean;
}

export function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onRenameSession,
  onSearch,
  onOpenSettings,
  loading,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearch, setShowSearch] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const { user } = useAuth();

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    onSearch(value);
  };

  const startEditing = (sessionId: string, title: string) => {
    setEditingId(sessionId);
    setEditingTitle(title);
  };

  const commitEdit = () => {
    if (editingId && editingTitle.trim()) {
      onRenameSession(editingId, editingTitle.trim());
    }
    setEditingId(null);
    setEditingTitle("");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditingTitle("");
  };

  return (
    <TooltipProvider delayDuration={300}>
      <div
        className={cn(
          "flex h-full flex-col border-r border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 transition-all duration-300",
          collapsed ? "w-[56px]" : "w-[280px]",
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 px-2 py-3">
          {!collapsed && (
            <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 pl-1">对话历史</h2>
          )}
          <div className={cn("flex items-center gap-1", collapsed && "flex-col w-full")}>
            {collapsed ? (
              <>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => setCollapsed(false)}
                    >
                      <PanelLeftOpen className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right">展开侧边栏</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={onNewChat}
                    >
                      <SquarePen className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right">新建对话</TooltipContent>
                </Tooltip>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setCollapsed(true)}
                >
                  <PanelLeftClose className="h-4 w-4" />
                </Button>
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
              </>
            )}
          </div>
        </div>

        {/* Search */}
        {showSearch && !collapsed && (
          <div className="border-b border-slate-200 dark:border-slate-800 px-3 py-2">
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
                  className={cn(
                    "animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700",
                    collapsed ? "h-8 w-8 mx-auto" : "h-10",
                  )}
                />
              ))}
            </div>
          ) : sessions.length === 0 ? (
            !collapsed && (
              <p className="px-3 py-8 text-center text-sm text-slate-400 dark:text-slate-500">
                暂无对话
              </p>
            )
          ) : (
            <div className="space-y-0.5">
              {sessions.map((session) =>
                collapsed ? (
                  <Tooltip key={session.session_id}>
                    <TooltipTrigger asChild>
                      <div
                        className={cn(
                          "flex items-center justify-center rounded-lg p-2 cursor-pointer transition-colors",
                          currentSessionId === session.session_id
                            ? "bg-slate-200 dark:bg-slate-800 text-slate-900 dark:text-slate-100"
                            : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800",
                        )}
                        onClick={() => onSelectSession(session.session_id)}
                      >
                        <MessageSquare className="h-4 w-4 shrink-0 text-slate-400 dark:text-slate-500" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="right">{session.title}</TooltipContent>
                  </Tooltip>
                ) : (
                  <div
                    key={session.session_id}
                    className={cn(
                      "group flex items-center rounded-lg px-3 py-2 text-sm transition-colors cursor-pointer",
                      currentSessionId === session.session_id
                        ? "bg-slate-200 text-slate-900"
                        : "text-slate-600 hover:bg-slate-100",
                    )}
                    onClick={() => {
                      if (editingId !== session.session_id) {
                        onSelectSession(session.session_id);
                      }
                    }}
                  >
                    <MessageSquare className="mr-2 h-4 w-4 shrink-0 text-slate-400" />
                    {editingId === session.session_id ? (
                      <input
                        className="flex-1 min-w-0 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded px-1.5 py-0.5 text-sm outline-none focus:ring-1 focus:ring-slate-400"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") commitEdit();
                          if (e.key === "Escape") cancelEdit();
                        }}
                        onBlur={commitEdit}
                        autoFocus
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <span
                        className="flex-1 truncate"
                        onDoubleClick={(e) => {
                          e.stopPropagation();
                          startEditing(session.session_id, session.title);
                        }}
                      >
                        {session.title}
                      </span>
                    )}
                    {editingId === session.session_id ? (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 shrink-0 ml-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          commitEdit();
                        }}
                      >
                        <Check className="h-3 w-3 text-slate-500" />
                      </Button>
                    ) : (
                      <div className="flex shrink-0 opacity-0 group-hover:opacity-100">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={(e) => {
                            e.stopPropagation();
                            startEditing(session.session_id, session.title);
                          }}
                        >
                          <Pencil className="h-3 w-3 text-slate-400" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteSession(session.session_id);
                          }}
                        >
                          <Trash2 className="h-3 w-3 text-slate-400" />
                        </Button>
                      </div>
                    )}
                  </div>
                ),
              )}
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="border-t border-slate-200 dark:border-slate-800 px-2 py-3">
          {collapsed ? (
            <div className="flex flex-col items-center">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-700 text-xs font-medium text-slate-600 dark:text-slate-300 cursor-default">
                    {user?.nickname?.charAt(0) || "U"}
                  </div>
                </TooltipTrigger>
                <TooltipContent side="right">{user?.nickname || "用户"}</TooltipContent>
              </Tooltip>
            </div>
          ) : (
            <div className="flex items-center justify-between px-1">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-700 text-xs font-medium text-slate-600 dark:text-slate-300">
                  {user?.nickname?.charAt(0) || "U"}
                </div>
                <span className="text-sm text-slate-600 dark:text-slate-400 truncate max-w-[140px]">
                  {user?.nickname || "用户"}
                </span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={onOpenSettings}
              >
                <Settings className="h-4 w-4 text-slate-400" />
              </Button>
            </div>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
}
