"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface User {
  user_id: string;
  email?: string;
  nickname: string | null;
  theme: string;
  font_size: string;
  bubble_style: string;
  gen_auto_mode: number;
  gen_security_weight: string;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  updateUser: (partial: Partial<User>) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

function applyTheme(theme: string) {
  if (theme === "system") {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.toggle("dark", prefersDark);
  } else {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (savedToken && savedUser) {
      const parsed = JSON.parse(savedUser);
      setToken(savedToken);
      setUser(parsed);
      applyTheme(parsed.theme || "system");
    }
    setIsLoading(false);
  }, []);

  // Listen for system theme changes when theme is "system"
  useEffect(() => {
    if (user?.theme !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (e: MediaQueryListEvent) => {
      document.documentElement.classList.toggle("dark", e.matches);
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [user?.theme]);

  function setAuth(newToken: string, newUser: User) {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem("token", newToken);
    localStorage.setItem("user", JSON.stringify(newUser));
    document.cookie = `token=${newToken}; path=/; max-age=${72 * 3600}; SameSite=Lax`;
    applyTheme(newUser.theme || "system");
  }

  function updateUser(partial: Partial<User>) {
    if (!user || !token) return;
    const updated = { ...user, ...partial };
    setUser(updated);
    localStorage.setItem("user", JSON.stringify(updated));
    if (partial.theme !== undefined) {
      applyTheme(partial.theme);
    }
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    document.cookie = "token=; path=/; max-age=0";
    document.documentElement.classList.remove("dark");
    router.push("/auth/login");
  }

  return (
    <AuthContext.Provider value={{ token, user, setAuth, updateUser, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
