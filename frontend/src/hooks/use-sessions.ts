"use client";

import { useState, useEffect, useCallback } from "react";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";

export interface Session {
  session_id: string;
  title: string;
  created_at: string;
  updated_at?: string;
}

interface SessionsResponse {
  sessions: Session[];
}

interface CreateSessionResponse {
  session_id: string;
  title: string;
  created_at: string;
}

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSessions = useCallback(async (search?: string) => {
    setLoading(true);
    try {
      const query = search ? `?search=${encodeURIComponent(search)}` : "";
      const res = await apiGet<SessionsResponse>(`/api/sessions${query}`);
      setSessions(res.sessions);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createSession = useCallback(async (): Promise<string> => {
    const res = await apiPost<CreateSessionResponse>("/api/sessions", {});
    setSessions((prev) => [
      { ...res, updated_at: res.created_at },
      ...prev,
    ]);
    return res.session_id;
  }, []);

  const renameSession = useCallback(async (sessionId: string, title: string) => {
    await apiPut(`/api/sessions/${sessionId}/title`, { title });
    setSessions((prev) =>
      prev.map((s) => (s.session_id === sessionId ? { ...s, title } : s))
    );
  }, []);

  const deleteSession = useCallback(async (sessionId: string) => {
    await apiDelete(`/api/sessions/${sessionId}`);
    setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    sessions,
    loading,
    fetchSessions,
    createSession,
    renameSession,
    deleteSession,
  };
}
