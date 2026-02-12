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
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [children]);

  return (
    <div
      ref={containerRef}
      className={`flex-1 overflow-y-auto px-4 py-6 ${className ?? ""}`}
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {children}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
