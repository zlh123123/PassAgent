"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/ui/password-input";
import { useAuth } from "@/providers/Auth";
import { sendCode, register } from "@/lib/auth-api";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [error, setError] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuth();
  const router = useRouter();

  async function handleSendCode() {
    if (!email) {
      setError("请输入邮箱");
      return;
    }
    setError("");
    try {
      const res = await sendCode(email);
      setCodeSent(true);
      setCountdown(Math.floor(res.expires_in / 5)); // 60s cooldown
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "发送验证码失败");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }
    if (password.length < 6) {
      setError("密码长度至少6位");
      return;
    }

    setLoading(true);
    try {
      const res = await register(email, code, password, nickname || undefined);
      setAuth(res.token, {
        user_id: res.user_id,
        nickname: nickname || null,
        theme: "light",
      });
      router.push("/chat");
    } catch (err) {
      setError(err instanceof Error ? err.message : "注册失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-slate-900">注册 PassAgent</h1>
          <p className="text-sm text-slate-500 mt-2">创建账户，开始使用智能口令助手</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="nickname">昵称（可选）</Label>
            <Input
              id="nickname"
              placeholder="你的昵称"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">邮箱</Label>
            <div className="flex gap-2">
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Button
                type="button"
                variant="outline"
                className="shrink-0"
                onClick={handleSendCode}
                disabled={countdown > 0}
              >
                {countdown > 0 ? `${countdown}s` : codeSent ? "重新发送" : "发送验证码"}
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="code">验证码</Label>
            <Input
              id="code"
              placeholder="输入6位验证码"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              maxLength={6}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">密码</Label>
            <PasswordInput
              id="password"
              placeholder="至少6位密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">确认密码</Label>
            <PasswordInput
              id="confirmPassword"
              placeholder="再次输入密码"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "注册中..." : "注册"}
          </Button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          已有账户？{" "}
          <Link href="/auth/login" className="text-slate-900 font-medium hover:underline">
            登录
          </Link>
        </p>
      </div>
    </div>
  );
}
