"use client";

import { useCallback, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Sidebar } from "@/components/chat/sidebar";
import { SettingsDialog } from "@/components/chat/settings-dialog";
import { useSessions } from "@/hooks/use-sessions";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [settingsOpen, setSettingsOpen] = useState(false);

  const { sessions, loading, fetchSessions, createSession, renameSession, deleteSession } =
    useSessions();

  // Extract current session ID from URL
  const match = pathname.match(/^\/chat\/(.+)$/);
  const currentSessionId = match ? match[1] : null;

  const handleNewChat = useCallback(async () => {
    // 如果当前已经在一个空白会话（title 仍为"新对话"）上，不再重复创建
    if (currentSessionId) {
      const current = sessions.find((s) => s.session_id === currentSessionId);
      if (current && current.title === "新对话") {
        return;
      }
    }
    const sessionId = await createSession();
    router.push(`/chat/${sessionId}`);
  }, [createSession, router, currentSessionId, sessions]);

  const handleSelectSession = useCallback(
    (sessionId: string) => {
      router.push(`/chat/${sessionId}`);
    },
    [router],
  );

  const handleDeleteSession = useCallback(
    async (sessionId: string) => {
      await deleteSession(sessionId);
      if (currentSessionId === sessionId) {
        router.push("/chat");
      }
    },
    [deleteSession, currentSessionId, router],
  );

  // Listen for session updates from chat messages
  useEffect(() => {
    const handleSessionUpdate = () => {
      fetchSessions();
    };

    window.addEventListener("session-updated", handleSessionUpdate);
    return () => {
      window.removeEventListener("session-updated", handleSessionUpdate);
    };
  }, [fetchSessions]);

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onRenameSession={renameSession}
        onSearch={(q) => fetchSessions(q)}
        onOpenSettings={() => setSettingsOpen(true)}
        loading={loading}
      />
      <main className="flex min-h-0 flex-1 flex-col overflow-hidden">{children}</main>
      <SettingsDialog open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  );
}
