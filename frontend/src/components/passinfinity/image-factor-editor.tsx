"use client";

import { useMemo, useRef, useState } from "react";
import { Grid2x2, Trash2, Undo2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ImageFactor } from "@/components/passinfinity/types";

export interface PresetImage {
  label: string;
  src: string;
  description: string;
}

interface Props {
  factor: ImageFactor;
  presets: PresetImage[];
  onChange: (factor: ImageFactor) => void;
  onRemove: () => void;
}

export function ImageFactorEditor({ factor, presets, onChange, onRemove }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [customUrl, setCustomUrl] = useState("");

  const tagText = useMemo(() => factor.tags.join(", "), [factor.tags]);

  function setField<K extends keyof ImageFactor>(key: K, value: ImageFactor[K]) {
    onChange({ ...factor, [key]: value });
  }

  function handleImageClick(event: React.MouseEvent<HTMLDivElement>) {
    if (!factor.src || !containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const rawX = (event.clientX - rect.left) / rect.width;
    const rawY = (event.clientY - rect.top) / rect.height;
    const gridSize = 5;
    const point = factor.use_grid
      ? {
          x: (Math.floor(rawX * gridSize) + 0.5) / gridSize,
          y: (Math.floor(rawY * gridSize) + 0.5) / gridSize,
          kind: "grid" as const,
        }
      : {
          x: rawX,
          y: rawY,
          kind: "passpoint" as const,
        };

    setField("points", [...factor.points, point]);
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between gap-4">
        <p className="text-sm text-slate-500">
          选择图片后点击添加记忆点；启用网格后自动吸附到 5×5 格心。
        </p>
        <Button variant="outline" size="sm" className="shrink-0 text-slate-500 hover:text-rose-600 hover:border-rose-200" onClick={onRemove}>
          <Trash2 className="mr-1.5 h-3.5 w-3.5" />
          移除
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            {presets.map((preset) => {
              const selected = factor.src === preset.src;
              return (
                <button
                  key={preset.src}
                  type="button"
                  onClick={() => setField("src", preset.src)}
                  className={`overflow-hidden rounded-lg border text-left transition ${
                    selected
                      ? "border-transparent ring-2 ring-violet-500 shadow-md"
                      : "border-slate-200 hover:border-slate-300 hover:shadow-sm"
                  }`}
                >
                  <div className="aspect-[16/9] bg-slate-100">
                    <img src={preset.src} alt={preset.label} className="h-full w-full object-cover" />
                  </div>
                  <div className="space-y-1 p-3">
                    <p className="text-sm font-medium text-slate-900">{preset.label}</p>
                    <p className="text-xs leading-relaxed text-slate-500">{preset.description}</p>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="flex gap-2">
            <Input
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              placeholder="或输入远程图片 URL"
              className="text-sm"
            />
            <Button
              type="button"
              variant="outline"
              className="shrink-0"
              onClick={() => {
                if (customUrl.trim()) setField("src", customUrl.trim());
              }}
            >
              应用
            </Button>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Checkbox
                  id={`grid-${factor.image_id}`}
                  checked={factor.use_grid}
                  onCheckedChange={(checked) => setField("use_grid", Boolean(checked))}
                />
                <Label htmlFor={`grid-${factor.image_id}`} className="text-sm text-slate-700">
                  启用 5x5 网格
                </Label>
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setField("points", factor.points.slice(0, -1))}
                  disabled={factor.points.length === 0}
                >
                  <Undo2 className="mr-2 h-4 w-4" />
                  撤销
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setField("points", [])}
                  disabled={factor.points.length === 0}
                >
                  清空选点
                </Button>
              </div>
            </div>

            <div
              ref={containerRef}
              onClick={handleImageClick}
              className="relative aspect-[16/9] cursor-crosshair overflow-hidden rounded-lg border border-slate-200 bg-slate-100 shadow-inner"
            >
              {factor.src ? (
                <>
                  <img
                    src={factor.src}
                    alt={factor.title || "PassInfinity preset"}
                    className="h-full w-full object-cover"
                  />
                  {factor.use_grid && (
                    <div
                      className="pointer-events-none absolute inset-0"
                      style={{
                        backgroundImage:
                          "linear-gradient(to right, rgba(15,23,42,0.18) 1px, transparent 1px), linear-gradient(to bottom, rgba(15,23,42,0.18) 1px, transparent 1px)",
                        backgroundSize: "20% 20%",
                      }}
                    />
                  )}
                  {factor.points.map((point, index) => (
                    <div
                      key={`${point.x}-${point.y}-${index}`}
                      className="pointer-events-none absolute flex h-7 w-7 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-2 border-white bg-violet-600 text-xs font-bold text-white shadow-lg"
                      style={{
                        left: `${point.x * 100}%`,
                        top: `${point.y * 100}%`,
                      }}
                    >
                      {index + 1}
                    </div>
                  ))}
                </>
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-3 px-6 text-center text-sm text-slate-500">
                  <Grid2x2 className="h-7 w-7 text-slate-400" />
                  先选择一张图片，再点击添加记忆点。
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-3 rounded-xl border border-slate-200 bg-slate-50/80 p-4">
          <div className="space-y-2">
            <Label htmlFor={`title-${factor.image_id}`} className="text-xs font-semibold uppercase tracking-wider text-slate-400">标题</Label>
            <Input
              id={`title-${factor.image_id}`}
              value={factor.title}
              onChange={(e) => setField("title", e.target.value)}
              placeholder="例如：城市草图"
              className="text-sm"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor={`tags-${factor.image_id}`} className="text-xs font-semibold uppercase tracking-wider text-slate-400">标签</Label>
            <Input
              id={`tags-${factor.image_id}`}
              value={tagText}
              onChange={(e) =>
                setField(
                  "tags",
                  e.target.value
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean),
                )
              }
              placeholder="landmark, travel"
              className="text-sm"
            />
            <p className="text-xs text-slate-400">用英文逗号分隔，便于后续解释。</p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">摘要</p>
            <div className="mt-2.5 space-y-1.5 text-xs text-slate-500">
              <p>已选图片：{factor.src ? <span className="text-emerald-600">是</span> : <span className="text-slate-400">否</span>}</p>
              <p>模式：{factor.use_grid ? "网格点选" : "自由点选"}</p>
              <p>记忆点：<span className="font-semibold text-slate-700">{factor.points.length}</span> 个</p>
              <p>标签：{factor.tags.length > 0 ? factor.tags.join(", ") : <span className="text-slate-400">未设置</span>}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
