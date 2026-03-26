"use client";

import { Shield, Zap, Code2, Search } from "lucide-react";

export default function ChatWelcomePage() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-6 py-12">
      <div className="mb-10 text-center">
        <h1 className="mb-2 text-3xl font-bold text-slate-900 dark:text-slate-100">PassAgent</h1>
        <p className="text-slate-500 dark:text-slate-400">基于LLM的口令安全智能助手</p>
      </div>

      <div className="grid w-full max-w-3xl gap-4 sm:grid-cols-2">
        {[
          {
            icon: Shield,
            title: "口令强度评估",
            desc: "分析口令安全性，给出评分和改进建议",
          },
          {
            icon: Zap,
            title: "智能口令生成",
            desc: "根据你的偏好生成安全且好记的口令",
          },
          {
            icon: Search,
            title: "泄露检测",
            desc: "检查口令是否在已知数据泄露中出现",
          },
          {
            icon: Code2,
            title: "口令恢复",
            desc: "通过记忆片段帮你找回遗忘的口令",
          },
        ].map((item, i) => (
          <div
            key={i}
            className="rounded-2xl border border-slate-200 dark:border-slate-700 p-5 transition-colors hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800/50"
          >
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-800">
              <item.icon className="h-5 w-5 text-slate-500 dark:text-slate-300" />
            </div>
            <h3 className="mb-2 text-sm font-medium text-slate-800 dark:text-slate-200">
              {item.title}
            </h3>
            <p className="text-xs leading-6 text-slate-500 dark:text-slate-400">{item.desc}</p>
          </div>
        ))}
      </div>

      <p className="mt-8 text-sm text-slate-400 dark:text-slate-500">
        点击左侧「新建对话」开始使用
      </p>
    </div>
  );
}
