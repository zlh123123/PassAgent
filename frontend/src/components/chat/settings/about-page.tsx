"use client";

import Image from "next/image";
import { ExternalLink } from "lucide-react";

const REPO_URL = "https://github.com/zlh123123/PassAgent";

const projectInfo = [
  { label: "版本号", value: "v1.0.0" },
  { label: "开源协议", value: "MIT License", href: `${REPO_URL}/blob/main/LICENSE` },
  { label: "项目仓库", value: "GitHub", href: REPO_URL },
  { label: "问题反馈", value: "GitHub Issues", href: `${REPO_URL}/issues` },
];

export function AboutPage() {
  return (
    <div className="space-y-6">
      {/* Logo + 标题 */}
      <div className="flex flex-col items-center text-center pt-2 pb-2">
        <Image src="/favicon.ico" alt="PassAgent" width={64} height={64} className="mb-3" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">PassAgent v1.0</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          基于大语言模型的个人全能口令助手
        </p>
      </div>

      {/* 项目信息 */}
      <div>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">项目信息</p>
        <div className="rounded-lg border border-slate-200 dark:border-slate-700 divide-y divide-slate-200 dark:divide-slate-700">
          {projectInfo.map((item) => (
            <div key={item.label} className="flex items-center justify-between px-4 py-3">
              <span className="text-sm text-slate-600 dark:text-slate-400">{item.label}</span>
              {item.href ? (
                <a
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-slate-900 dark:text-slate-100 hover:underline flex items-center gap-1"
                >
                  {item.value}
                  <ExternalLink className="h-3 w-3" />
                </a>
              ) : (
                <span className="text-sm text-slate-900 dark:text-slate-100">{item.value}</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 第三方服务与致谢 */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-5">
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">第三方服务与致谢</p>
        <ul className="text-xs text-slate-500 dark:text-slate-400 space-y-1.5 leading-relaxed">
          <li>
            <span className="font-medium text-slate-600 dark:text-slate-300">Have I Been Pwned API</span>
            {" "}— 泄露数据查询（k-Anonymity）
          </li>
          <li>
            <span className="font-medium text-slate-600 dark:text-slate-300">SiliconFlow</span>
            {" "}— 文本向量化服务
          </li>
          <li>
            前端模板基于{" "}
            <a
              href="https://github.com/langchain-ai/agent-chat-ui"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-slate-700 dark:hover:text-slate-300"
            >
              Brace Sproul 的开源项目
            </a>
            （MIT License）
          </li>
        </ul>
      </div>

      {/* 隐私说明 */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-5">
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">隐私说明</p>
        <ul className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed list-disc list-inside space-y-1 pl-1">
          <li>所有密码评估和生成均在服务端本地完成，不发送至第三方（HIBP 使用 k-Anonymity，仅发送哈希前 5 位）</li>
          <li>对话记录存储在服务端数据库中，不会用于模型训练</li>
          <li>你可以随时删除所有数据</li>
        </ul>
      </div>

      {/* 免责声明 */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-5">
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">免责声明</p>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          本工具仅供口令安全研究和个人使用，不对因使用本工具产生的任何直接或间接损失承担责任。
          生成的密码建议仅供参考，请用户自行评估后使用。
        </p>
      </div>

      {/* 版权 */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-4 text-center">
        <p className="text-xs text-slate-400 dark:text-slate-500">
          © 2026 Linghao Zhang. MIT License.
        </p>
      </div>
    </div>
  );
}
