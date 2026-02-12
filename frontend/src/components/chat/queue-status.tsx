"use client";

interface QueueStatusProps {
  position: number | null;
}

export function QueueStatus({ position }: QueueStatusProps) {
  if (position === null) return null;

  return (
    <div className="flex justify-center py-2">
      <div className="rounded-full bg-amber-50 dark:bg-amber-950 px-4 py-1.5 text-sm text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800">
        {position === 0
          ? "正在处理..."
          : `前方还有 ${position} 个任务，请稍候`}
      </div>
    </div>
  );
}
