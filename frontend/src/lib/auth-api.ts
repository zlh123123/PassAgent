const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export interface SendCodeResponse {
  message: string;
  expires_in: number;
}

export interface RegisterResponse {
  user_id: string;
  token: string;
  nickname: string | null;
  theme: string;
  font_size: string;
  bubble_style: string;
  gen_auto_mode: number;
  gen_security_weight: string;
}

export interface LoginResponse {
  user_id: string;
  token: string;
  nickname: string | null;
  theme: string;
  font_size: string;
  bubble_style: string;
  gen_auto_mode: number;
  gen_security_weight: string;
}

async function request<T>(
  path: string,
  body: Record<string, unknown>,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "请求失败" }));
    throw new Error(err.detail || "请求失败");
  }
  return res.json();
}

export function sendCode(email: string) {
  return request<SendCodeResponse>("/api/auth/send-code", { email });
}

export function register(
  email: string,
  code: string,
  password: string,
  nickname?: string,
) {
  return request<RegisterResponse>("/api/auth/register", {
    email,
    code,
    password,
    nickname,
  });
}

export function login(email: string, password: string) {
  return request<LoginResponse>("/api/auth/login", { email, password });
}
