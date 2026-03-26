import { redirect } from "next/navigation";

const VALID_MODES = new Set(["image", "map", "richtext"]);

export default async function PassInfinityModePage({
  params,
}: {
  params: Promise<{ mode: string }>;
}) {
  const { mode } = await params;
  if (!VALID_MODES.has(mode)) {
    redirect("/lab/passinfinity");
  }
  redirect("/lab/passinfinity");
}
