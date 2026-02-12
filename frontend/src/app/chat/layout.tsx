"use client";

import { useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Sidebar } from "@/components/chat/sidebar";
import { useSessions } from "@/hooks/use-sessions";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

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
    <div className="flex h-screen bg-white">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onSearch={(q) => fetchSessions(q)}
        loading={loading}
      />
      <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
    </div>
  );
}
