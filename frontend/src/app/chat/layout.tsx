"use client";

import { useCallback, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Sidebar } from "@/components/chat/sidebar";
import { SettingsPanel } from "@/components/chat/settings-panel";
import { useSessions } from "@/hooks/use-sessions";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [settingsOpen, setSettingsOpen] = useState(false);

  const { sessions, loading, fetchSessions, createSession, deleteSession } =
    useSessions();

  // Extract current session ID from URL
  const match = pathname.match(/^\/chat\/(.+)$/);
  const currentSessionId = match ? match[1] : null;

  const handleNewChat = useCallback(async () => {
    const sessionId = await createSession();
    router.push(`/chat/${sessionId}`);
  }, [createSession, router]);

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

  return (
    <div className="flex h-screen bg-white dark:bg-slate-950">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onSearch={(q) => fetchSessions(q)}
        onOpenSettings={() => setSettingsOpen(true)}
        loading={loading}
      />
      <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
      <SettingsPanel open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  );
}
