import { Suspense } from "react";
import { notFound } from "next/navigation";
import {
  PassInfinityBuilder,
  type BuilderMode,
} from "@/components/passinfinity/passinfinity-builder";

const VALID_MODES = new Set<BuilderMode>(["image", "map", "richtext"]);

export default async function PassInfinityModePage({
  params,
}: {
  params: Promise<{ mode: string }>;
}) {
  const { mode } = await params;
  if (!VALID_MODES.has(mode as BuilderMode)) {
    notFound();
  }

  return (
    <Suspense fallback={<div className="h-screen bg-slate-50" />}>
      <PassInfinityBuilder mode={mode as BuilderMode} />
    </Suspense>
  );
}
