"use client";

import { useAuth } from "@/providers/Auth";
import { apiPut } from "@/lib/api";
import { Slider } from "@/components/ui/slider";
import { Monitor, Sun, Moon } from "lucide-react";

const themes = [
  { value: "light", label: "浅色", icon: Sun },
  { value: "dark", label: "深色", icon: Moon },
  { value: "system", label: "系统", icon: Monitor },
] as const;

const fontSizes = [
  { value: "S", label: "S", css: "13px" },
  { value: "M", label: "M", css: "15px" },
  { value: "L", label: "L", css: "17px" },
  { value: "XL", label: "XL", css: "19px" },
] as const;

const bubbleStyles = [
  { value: "rounded", label: "圆润" },
  { value: "square", label: "方正" },
  { value: "minimal", label: "简约" },
] as const;

export function AppearancePage() {
  const { user, updateUser } = useAuth();

  const currentTheme = user?.theme || "system";
  const currentFontSize = user?.font_size || "M";
  const currentBubbleStyle = user?.bubble_style || "rounded";

  const fontSizeIndex = fontSizes.findIndex((f) => f.value === currentFontSize);

  const handleThemeChange = async (theme: string) => {
    updateUser({ theme });
    try {
      await apiPut("/api/user/profile", { theme });
    } catch {
      updateUser({ theme: currentTheme });
    }
  };

  const handleFontSizeChange = async (values: number[]) => {
    const size = fontSizes[values[0]].value;
    updateUser({ font_size: size });
    try {
      await apiPut("/api/user/profile", { font_size: size });
    } catch {
      updateUser({ font_size: currentFontSize });
    }
  };

  const handleBubbleStyleChange = async (style: string) => {
    updateUser({ bubble_style: style });
    try {
      await apiPut("/api/user/profile", { bubble_style: style });
    } catch {
      updateUser({ bubble_style: currentBubbleStyle });
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-base font-medium text-slate-900 dark:text-slate-100">外观</h3>

      {/* 主题 */}
      <div>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">主题模式</p>
        <div className="grid grid-cols-3 gap-2">
          {themes.map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.value}
                onClick={() => handleThemeChange(t.value)}
                className={`flex flex-col items-center gap-1.5 rounded-lg border p-3 transition-colors ${
                  currentTheme === t.value
                    ? "border-slate-900 dark:border-slate-100 bg-slate-50 dark:bg-slate-800"
                    : "border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-xs">{t.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 字体大小 */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-5">
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">字体大小</p>
        <div className="rounded-lg border border-slate-200 dark:border-slate-700 p-4">
          <div className="px-1">
            <Slider
              min={0}
              max={3}
              step={1}
              value={[fontSizeIndex >= 0 ? fontSizeIndex : 1]}
              onValueChange={handleFontSizeChange}
            />
            <div className="flex justify-between mt-2">
              {fontSizes.map((f) => (
                <span
                  key={f.value}
                  className={`text-xs ${
                    currentFontSize === f.value
                      ? "text-slate-900 dark:text-slate-100 font-medium"
                      : "text-slate-400 dark:text-slate-500"
                  }`}
                >
                  {f.label}
                </span>
              ))}
            </div>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-3 text-center">
            预览：<span style={{ fontSize: fontSizes[fontSizeIndex >= 0 ? fontSizeIndex : 1].css }}>这是一段示例文字</span>
          </p>
        </div>
      </div>

      {/* 气泡样式 */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-5">
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">气泡样式</p>
        <div className="grid grid-cols-3 gap-2">
          {bubbleStyles.map((s) => (
            <button
              key={s.value}
              onClick={() => handleBubbleStyleChange(s.value)}
              className={`rounded-lg border p-3 text-sm transition-colors ${
                currentBubbleStyle === s.value
                  ? "border-slate-900 dark:border-slate-100 bg-slate-50 dark:bg-slate-800"
                  : "border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60"
              }`}
            >
              <div className="flex flex-col gap-1.5 mb-2">
                <div
                  className={`h-4 w-3/4 ml-auto ${
                    s.value === "minimal"
                      ? "border-b border-slate-300 dark:border-slate-600"
                      : "bg-slate-800 dark:bg-slate-200"
                  } ${s.value === "rounded" ? "rounded-xl" : s.value === "square" ? "rounded-[3px]" : ""}`}
                />
                <div
                  className={`h-4 w-4/5 ${
                    s.value === "minimal"
                      ? "border-b border-slate-300 dark:border-slate-600"
                      : "bg-slate-200 dark:bg-slate-700"
                  } ${s.value === "rounded" ? "rounded-xl" : s.value === "square" ? "rounded-[3px]" : ""}`}
                />
              </div>
              <span className="text-xs">{s.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
