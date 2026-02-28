"use client";

import { useAuth } from "@/providers/Auth";
import { apiPut } from "@/lib/api";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";

const levels = [
  { name: "最高安全", alpha: "0.9", desc: "纯随机生成，适合密码管理器存储" },
  { name: "偏安全", alpha: "0.7", desc: "高随机性，适合银行金融类账号" },
  { name: "均衡", alpha: "0.5", desc: "兼顾安全与可记忆，适合日常账号" },
  { name: "偏好记", alpha: "0.3", desc: "较强记忆关联，适合高频手动输入场景" },
  { name: "最好记", alpha: "0.1", desc: "助记短语/可发音，适合低敏感度账号" },
];

const sliderLabels = ["最高安全", "偏安全", "均衡", "偏好记", "最好记"];

function weightToIndex(w: string): number {
  const v = parseFloat(w);
  if (v >= 0.85) return 0;
  if (v >= 0.6) return 1;
  if (v >= 0.4) return 2;
  if (v >= 0.2) return 3;
  return 4;
}

function indexToWeight(i: number): string {
  return ["0.9", "0.7", "0.5", "0.3", "0.1"][i];
}

export function GenerationPage() {
  const { user, updateUser } = useAuth();

  const autoMode = user?.gen_auto_mode ?? 1;
  const weightIndex = weightToIndex(user?.gen_security_weight || "0.5");
  const currentLevel = levels[weightIndex];

  const handleAutoModeChange = async (checked: boolean) => {
    const val = checked ? 1 : 0;
    updateUser({ gen_auto_mode: val });
    try {
      await apiPut("/api/user/profile", { gen_auto_mode: val });
    } catch {
      updateUser({ gen_auto_mode: autoMode });
    }
  };

  const handleWeightChange = async (values: number[]) => {
    const weight = indexToWeight(values[0]);
    updateUser({ gen_security_weight: weight });
    try {
      await apiPut("/api/user/profile", { gen_security_weight: weight });
    } catch {
      updateUser({ gen_security_weight: user?.gen_security_weight || "0.5" });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-base font-medium text-slate-900 dark:text-slate-100">口令生成</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          控制 Agent 生成口令时的策略倾向。
        </p>
      </div>

      {/* 自动模式 */}
      <div className="rounded-lg border border-slate-200 dark:border-slate-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">自动模式</span>
          </div>
          <Switch checked={autoMode === 1} onCheckedChange={handleAutoModeChange} />
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
          Agent 根据场景和你的记忆自动选择最佳生成策略
        </p>
      </div>

      {/* 手动档位 - 仅在关闭自动模式时显示 */}
      {autoMode !== 1 && (
        <div>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">手动档位</p>
          <div className="px-1 mb-2">
            <div className="flex justify-between text-sm mb-2">
              <span>安全优先</span>
              <span>好记优先</span>
            </div>
            <Slider
              min={0}
              max={4}
              step={1}
              value={[weightIndex]}
              onValueChange={handleWeightChange}
            />
            <div className="flex justify-between mt-1.5">
              {sliderLabels.map((label) => (
                <span key={label} className="text-[10px] text-slate-500 dark:text-slate-400">
                  {label}
                </span>
              ))}
            </div>
          </div>

          {/* 当前档位详情 */}
          <div className="rounded-lg border border-slate-200 dark:border-slate-700 p-3 mt-4">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                当前：{currentLevel.name}
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {currentLevel.desc}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
