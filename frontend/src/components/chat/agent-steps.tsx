"use client";

import { type AgentStep } from "@/hooks/use-chat";
import { CheckCircle2, Loader2 } from "lucide-react";

interface AgentStepsProps {
  steps: AgentStep[];
  isStreaming: boolean;
}

function StepIcon({ step, isLast, isStreaming }: { step: AgentStep; isLast: boolean; isStreaming: boolean }) {
  // If step has summary, it's completed
  if (step.summary) {
    return <CheckCircle2 className="h-4 w-4 shrink-0 text-green-500" />;
  }
  // If it's the last step and still streaming, show spinner
  if (isLast && isStreaming) {
    return <Loader2 className="h-4 w-4 shrink-0 animate-spin text-slate-400" />;
  }
  return <CheckCircle2 className="h-4 w-4 shrink-0 text-green-500" />;
}

function formatStepText(step: AgentStep): string {
  if (step.node === "planner" && step.action) {
    if (step.action === "respond") return "准备生成回复";
    return `决定调用 ${step.action}`;
  }
  if (step.summary) {
    const entries = Object.entries(step.summary);
    if (entries.length === 0) return `${step.node} 完成`;
    const summaryText = entries
      .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
      .join(", ");
    return `${step.node} → ${summaryText}`;
  }
  if (step.reasoning) {
    return `${step.node}: ${step.reasoning}`;
  }
  return step.node;
}

export function AgentSteps({ steps, isStreaming }: AgentStepsProps) {
  if (steps.length === 0) return null;

  return (
    <div className="mb-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 p-3">
      <p className="mb-2 text-xs font-medium text-slate-500 dark:text-slate-400">Agent 执行步骤</p>
      <div className="space-y-1.5">
        {steps.map((step, i) => (
          <div key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
            <StepIcon step={step} isLast={i === steps.length - 1} isStreaming={isStreaming} />
            <span className="leading-5">{formatStepText(step)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
