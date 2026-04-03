"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowRight, Compass, ImagePlus, Type } from "lucide-react";
import { Button } from "@/components/ui/button";

const ENTRY_CARDS = [
  {
    href: "/lab/passinfinity/image",
    title: "图片记忆点",
    description: "在图片上按顺序点击记忆点，适合路径、轮廓和视觉记忆。",
    icon: ImagePlus,
    accent: "from-violet-500/10 to-violet-500/5 border-violet-200 hover:border-violet-300 hover:shadow-violet-100",
    iconBg: "bg-violet-100 text-violet-700",
    tag: "视觉",
    tagColor: "bg-violet-100 text-violet-600",
  },
  {
    href: "/lab/passinfinity/map",
    title: "地图位置因子",
    description: "在地图上标记熟悉的位置，用空间顺序构造因子。",
    icon: Compass,
    accent: "from-emerald-500/10 to-emerald-500/5 border-emerald-200 hover:border-emerald-300 hover:shadow-emerald-100",
    iconBg: "bg-emerald-100 text-emerald-700",
    tag: "空间",
    tagColor: "bg-emerald-100 text-emerald-600",
  },
  {
    href: "/lab/passinfinity/richtext",
    title: "富文本标记",
    description: "通过文本内容和样式强调方式，构造只对你有意义的标记。",
    icon: Type,
    accent: "from-amber-500/10 to-amber-500/5 border-amber-200 hover:border-amber-300 hover:shadow-amber-100",
    iconBg: "bg-amber-100 text-amber-700",
    tag: "语义",
    tagColor: "bg-amber-100 text-amber-600",
  },
];

export default function PassInfinityEntryPage() {
  const searchParams = useSearchParams();
  const returnTo = searchParams.get("returnTo") || "/chat";

  return (
    <div className="h-screen overflow-y-auto bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-5xl px-6 py-14">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-2xl">
            <p className="text-sm uppercase tracking-[0.24em] text-slate-400">PassInfinity</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              选择一种因子开始
            </h1>
            <p className="mt-3 text-sm leading-7 text-slate-500">
              图片记忆点、地图位置因子和富文本标记已经拆成三个独立页面。先选一种进入，
              保存后 agent 可以继续读取并解释你的结果。
            </p>
          </div>

          <div className="flex gap-3">
            <Link href="/">
              <Button variant="outline" className="border-slate-200 text-slate-600 hover:text-slate-900">返回首页</Button>
            </Link>
            <Link href={returnTo}>
              <Button className="bg-slate-900 text-white hover:bg-slate-700">回到对话</Button>
            </Link>
          </div>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {ENTRY_CARDS.map((card) => {
            const Icon = card.icon;
            const href = `${card.href}?returnTo=${encodeURIComponent(returnTo)}`;
            return (
              <Link key={card.href} href={href}>
                <div
                  className={`group relative h-full overflow-hidden rounded-2xl border bg-gradient-to-br p-6 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${card.accent}`}
                >
                  <div className="flex items-start justify-between">
                    <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${card.iconBg}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${card.tagColor}`}>
                      {card.tag}
                    </span>
                  </div>
                  <h2 className="mt-5 text-base font-semibold text-slate-900">{card.title}</h2>
                  <p className="mt-1.5 text-sm leading-6 text-slate-500">{card.description}</p>
                  <div className="mt-5 flex items-center gap-1 text-sm font-medium text-slate-600 transition-all group-hover:gap-1.5 group-hover:text-slate-900">
                    进入
                    <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
