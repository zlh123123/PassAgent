"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { LockKeyhole, Save, Trash2 } from "lucide-react";
import { useAuth } from "@/providers/Auth";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  ImageFactorEditor,
  type PresetImage,
} from "@/components/passinfinity/image-factor-editor";
import { MapFactorEditor } from "@/components/passinfinity/map-factor-editor";
import type {
  ImageFactor,
  PassInfinityAnalysis,
  PassInfinityArtifact,
  PassInfinityDraft,
  RichTextStyle,
} from "@/components/passinfinity/types";
import {
  getPassInfinityArtifact,
  listPassInfinityArtifacts,
  savePassInfinityArtifact,
  validatePassInfinityDraft,
} from "@/lib/passinfinity-api";

export type BuilderMode = "image" | "map" | "richtext";

const PRESET_IMAGES: PresetImage[] = [
  {
    label: "City Grid",
    src: "/passinfinity/city-grid.svg",
    description: "路径、建筑和窗口类记忆点。",
  },
  {
    label: "Garden Memory",
    src: "/passinfinity/garden-memory.svg",
    description: "区域、节点和轮廓类记忆点。",
  },
  {
    label: "Orbit Memory",
    src: "/passinfinity/orbit-memory.svg",
    description: "层级、轨迹和中心点类记忆点。",
  },
];

const STYLE_OPTIONS: { value: RichTextStyle; label: string }[] = [
  { value: "bold", label: "加粗" },
  { value: "italic", label: "斜体" },
  { value: "underline", label: "下划线" },
  { value: "strikethrough", label: "删除线" },
];

const TABS: { mode: BuilderMode; label: string }[] = [
  { mode: "image", label: "图片记忆点" },
  { mode: "map", label: "地图位置" },
  { mode: "richtext", label: "富文本标记" },
];

function makeId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function createEmptyImageFactor(): ImageFactor {
  return {
    image_id: makeId(),
    title: "",
    src: PRESET_IMAGES[0].src,
    tags: [],
    use_grid: false,
    points: [],
  };
}

function createEmptyDraft(mode: BuilderMode): PassInfinityDraft {
  return {
    title: "",
    text: "",
    rich_text: { content: "", styles: [] },
    images: mode === "image" ? [createEmptyImageFactor()] : [],
    locations: [],
  };
}

function inferMode(draft: PassInfinityDraft): BuilderMode {
  if (draft.images.length > 0) return "image";
  if (draft.locations.length > 0) return "map";
  return "richtext";
}

interface Props {
  mode?: BuilderMode;
}

export function PassInfinityBuilder({ mode: initialMode }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { token, isLoading: authLoading } = useAuth();
  const artifactId = searchParams.get("artifactId");

  const [mode, setMode] = useState<BuilderMode>(initialMode ?? "image");
  const [draft, setDraft] = useState<PassInfinityDraft>(() => createEmptyDraft(mode));
  const [analysis, setAnalysis] = useState<PassInfinityAnalysis | null>(null);
  const [artifacts, setArtifacts] = useState<PassInfinityArtifact[]>([]);
  const [pageError, setPageError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [loadingArtifact, setLoadingArtifact] = useState(false);

  useEffect(() => {
    if (artifactId && token) {
      setLoadingArtifact(true);
      getPassInfinityArtifact(artifactId)
        .then((artifact) => {
          const inferredMode = inferMode(artifact.normalized_content);
          setMode(inferredMode);
          setDraft(artifact.normalized_content);
          setAnalysis({
            normalized_content: artifact.normalized_content,
            encoded_text: artifact.encoded_text,
            policy_result: artifact.policy_result,
          });
        })
        .catch((error) => {
          setPageError(error.message || "加载失败");
        })
        .finally(() => setLoadingArtifact(false));
    }
  }, [artifactId, token]);

  useEffect(() => {
    if (!token) {
      setArtifacts([]);
      return;
    }
    listPassInfinityArtifacts()
      .then((res) => setArtifacts(res.artifacts))
      .catch(() => {});
  }, [token, saveMessage]);

  useEffect(() => {
    setPageError("");
    const timer = window.setTimeout(() => {
      validatePassInfinityDraft(draft)
        .then((result) => setAnalysis(result))
        .catch((error) => {
          setPageError(error.message || "生成预览失败");
        });
    }, 300);
    return () => window.clearTimeout(timer);
  }, [draft]);

  function switchMode(next: BuilderMode) {
    setMode(next);
    setDraft(createEmptyDraft(next));
    setSaveMessage("");
    setPageError("");
    router.replace("/lab/passinfinity");
  }

  function updateDraft(patch: Partial<PassInfinityDraft>) {
    setDraft((current) => ({ ...current, ...patch }));
  }

  function toggleStyle(style: RichTextStyle, checked: boolean) {
    const nextStyles = checked
      ? [...draft.rich_text.styles, style]
      : draft.rich_text.styles.filter((item) => item !== style);
    updateDraft({ rich_text: { ...draft.rich_text, styles: nextStyles } });
  }

  async function handleSave() {
    if (!token) {
      setSaveMessage("请先登录再保存。");
      return;
    }
    setSaving(true);
    setSaveMessage("");
    try {
      const artifact = await savePassInfinityArtifact(draft);
      const inferredMode = inferMode(artifact.normalized_content);
      setArtifacts((current) => [
        artifact,
        ...current.filter((item) => item.artifact_id !== artifact.artifact_id),
      ]);
      setAnalysis({
        normalized_content: artifact.normalized_content,
        encoded_text: artifact.encoded_text,
        policy_result: artifact.policy_result,
      });
      router.replace(`/lab/passinfinity?artifactId=${artifact.artifact_id}`);
      setSaveMessage("已保存，agent 现在可以读取。");
    } catch (error) {
      setSaveMessage(error instanceof Error ? error.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  const warnings = analysis?.policy_result.warnings ?? [];
  const valid = analysis?.policy_result.valid ?? false;

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-white text-slate-900">
      {/* 顶栏 */}
      <header className="flex shrink-0 items-center justify-between border-b border-slate-200 px-5 py-3">
        <div className="flex items-center gap-4">
          <span className="text-sm font-semibold text-slate-900">PassInfinity</span>
          <nav className="flex items-center gap-1">
            {TABS.map((tab) => (
              <button
                key={tab.mode}
                type="button"
                onClick={() => switchMode(tab.mode)}
                className={`rounded px-3 py-1.5 text-sm transition ${
                  mode === tab.mode
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/chat">
            <Button variant="outline" size="sm">回到对话</Button>
          </Link>
          <Button
            size="sm"
            onClick={handleSave}
            disabled={saving || authLoading || !valid}
            className="bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-40"
          >
            <Save className="mr-1.5 h-3.5 w-3.5" />
            {saving ? "保存中…" : "保存"}
          </Button>
        </div>
      </header>

      {/* 主区域：左编辑 + 右侧边栏 */}
      <div className="flex min-h-0 flex-1">
        {/* 左侧：编辑器 */}
        <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-5">
          {/* 标题行 */}
          <div className="mb-4 flex items-center gap-3">
            <Input
              value={draft.title}
              onChange={(e) => updateDraft({ title: e.target.value })}
              placeholder="方案标题（可选）"
              className="h-8 max-w-xs text-sm"
            />
          </div>

          {/* image 编辑器 */}
          {mode === "image" && (
            <div className="space-y-3">
              {draft.images.map((factor, index) => (
                <ImageFactorEditor
                  key={factor.image_id}
                  factor={factor}
                  presets={PRESET_IMAGES}
                  onChange={(next) =>
                    updateDraft({
                      images: draft.images.map((item, i) => (i === index ? next : item)),
                    })
                  }
                  onRemove={() =>
                    updateDraft({
                      images:
                        draft.images.length === 1
                          ? [createEmptyImageFactor()]
                          : draft.images.filter((item) => item.image_id !== factor.image_id),
                    })
                  }
                />
              ))}
              <button
                type="button"
                onClick={() => updateDraft({ images: [...draft.images, createEmptyImageFactor()] })}
                className="w-full rounded border border-dashed border-slate-300 py-2 text-sm text-slate-500 hover:border-slate-400 hover:text-slate-700"
              >
                + 再加一张图片
              </button>
            </div>
          )}

          {/* map 编辑器 */}
          {mode === "map" && (
            <MapFactorEditor
              locations={draft.locations}
              onChange={(locations) => updateDraft({ locations })}
            />
          )}

          {/* richtext 编辑器 */}
          {mode === "richtext" && (
            <div className="grid gap-4 lg:grid-cols-2">
              <div className="space-y-3">
                <div>
                  <Label htmlFor="plain-text" className="text-sm text-slate-700">辅助文本</Label>
                  <Textarea
                    id="plain-text"
                    value={draft.text}
                    onChange={(e) => updateDraft({ text: e.target.value })}
                    placeholder="一句只有你知道怎么断句的短语"
                    className="mt-1.5 min-h-[120px] resize-none text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="rich-text" className="text-sm text-slate-700">核心标记</Label>
                  <Textarea
                    id="rich-text"
                    value={draft.rich_text.content}
                    onChange={(e) =>
                      updateDraft({ rich_text: { ...draft.rich_text, content: e.target.value } })
                    }
                    placeholder="某段只在你脑海里有特殊重音的话"
                    className="mt-1.5 min-h-[160px] resize-none text-sm"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-sm text-slate-700">样式标记</p>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    {STYLE_OPTIONS.map((option) => (
                      <label
                        key={option.value}
                        className="flex cursor-pointer items-center gap-2 rounded border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                      >
                        <Checkbox
                          checked={draft.rich_text.styles.includes(option.value)}
                          onCheckedChange={(checked) => toggleStyle(option.value, Boolean(checked))}
                        />
                        {option.label}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 右侧边栏 */}
        <aside className="flex w-64 shrink-0 flex-col gap-0 overflow-y-auto border-l border-slate-200">
          {/* 结果预览 */}
          <div className="border-b border-slate-200 p-4">
            <p className="mb-2 text-xs font-medium text-slate-500">编码预览</p>
            <pre className="max-h-28 overflow-auto whitespace-pre-wrap break-all rounded bg-slate-50 p-2 text-xs leading-5 text-slate-700">
              {analysis?.encoded_text || "等待输入…"}
            </pre>
          </div>

          {/* 状态 */}
          <div className="border-b border-slate-200 p-4">
            <p className="mb-2 text-xs font-medium text-slate-500">状态</p>
            <div
              className={`inline-flex items-center gap-1.5 rounded px-2 py-1 text-xs font-medium ${
                valid ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
              }`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${valid ? "bg-emerald-500" : "bg-amber-400"}`} />
              {valid ? "可保存" : "还需补充"}
            </div>
            {analysis?.policy_result.summary && (
              <p className="mt-2 text-xs leading-5 text-slate-600">{analysis.policy_result.summary}</p>
            )}
            {analysis?.policy_result.factors_used && analysis.policy_result.factors_used.length > 0 && (
              <p className="mt-1 text-xs text-slate-500">
                启用：{analysis.policy_result.factors_used.join(", ")}
              </p>
            )}
          </div>

          {/* 警告 */}
          {warnings.length > 0 && (
            <div className="border-b border-slate-200 p-4">
              <p className="mb-2 text-xs font-medium text-slate-500">提示</p>
              <div className="space-y-1.5">
                {warnings.map((w, i) => (
                  <p key={i} className="text-xs leading-5 text-amber-700">{w}</p>
                ))}
              </div>
            </div>
          )}

          {/* 保存信息 */}
          {(saveMessage || pageError) && (
            <div className="border-b border-slate-200 p-4">
              {saveMessage && <p className="text-xs text-slate-700">{saveMessage}</p>}
              {pageError && <p className="text-xs text-rose-600">{pageError}</p>}
            </div>
          )}

          {/* 登录提示 */}
          {!token && (
            <div className="border-b border-slate-200 p-4">
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <LockKeyhole className="h-3.5 w-3.5 shrink-0" />
                <span>登录后才能保存，agent 只会读取你自己的结果。</span>
              </div>
              <Link href="/auth/login" className="mt-2 block">
                <Button variant="outline" size="sm" className="w-full text-xs">去登录</Button>
              </Link>
            </div>
          )}

          {/* 已保存列表 */}
          <div className="flex-1 p-4">
            <p className="mb-2 text-xs font-medium text-slate-500">已保存</p>
            {!token && (
              <p className="text-xs text-slate-400">登录后显示</p>
            )}
            {token && artifacts.length === 0 && !loadingArtifact && (
              <p className="text-xs text-slate-400">还没有保存过结果</p>
            )}
            <div className="space-y-1.5">
              {artifacts.map((artifact) => {
                const inferredMode = inferMode(artifact.normalized_content);
                const isActive = artifactId === artifact.artifact_id;
                return (
                  <button
                    key={artifact.artifact_id}
                    type="button"
                    onClick={() => {
                      setMode(inferredMode);
                      setDraft(artifact.normalized_content);
                      setAnalysis({
                        normalized_content: artifact.normalized_content,
                        encoded_text: artifact.encoded_text,
                        policy_result: artifact.policy_result,
                      });
                      router.replace(`/lab/passinfinity?artifactId=${artifact.artifact_id}`);
                    }}
                    className={`group w-full rounded border p-2.5 text-left text-xs transition ${
                      isActive
                        ? "border-slate-900 bg-slate-900 text-white"
                        : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                    }`}
                  >
                    <p className={`truncate font-medium ${isActive ? "text-white" : "text-slate-800"}`}>
                      {artifact.title || "未命名"}
                    </p>
                    <p className={`mt-0.5 ${isActive ? "text-slate-400" : "text-slate-400"}`}>
                      {artifact.updated_at?.slice(0, 16).replace("T", " ") || ""}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
