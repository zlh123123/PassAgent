"use client";

import { useRef, useEffect, ReactNode } from "react";

interface MessageListProps {
  children: ReactNode;
  className?: string;
}

export function MessageList({ children, className }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 用 scrollTop 代替 scrollIntoView，避免冒泡滚动父容器
    const container = containerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [children]);

  return (
    <div
      ref={containerRef}
      className={`min-h-0 flex-1 overflow-y-auto px-4 py-6 ${className ?? ""}`}
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {children}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
