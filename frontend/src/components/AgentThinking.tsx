'use client'

import { Brain, Code, Database, Rocket, Wrench } from 'lucide-react'
import type { StepType } from '@/types'

interface AgentThinkingProps {
  step: StepType
  message: string
}

const stepIcons: Record<StepType, typeof Brain> = {
  analyzing: Database,
  planning: Brain,
  coding: Code,
  executing: Rocket,
  fixing: Wrench,
}

export function AgentThinking({ step, message }: AgentThinkingProps) {
  const Icon = stepIcons[step]

  return (
    <div className="flex items-start gap-4 pl-2 pr-4 py-2">
      <div className="w-6 h-6 rounded-full bg-[#1a1a1a] flex items-center justify-center mt-px shrink-0">
        <Icon className="w-3.5 h-3.5 text-[#737373]" />
      </div>
      <div className="flex-1 min-w-0 pt-0.5">
        <div className="flex items-center gap-2 mb-px">
          <div className="flex gap-1">
            <div className="w-1 h-1 bg-[#525252] rounded-full animate-pulse" />
            <div className="w-1 h-1 bg-[#525252] rounded-full animate-pulse [animation-delay:120ms]" />
            <div className="w-1 h-1 bg-[#525252] rounded-full animate-pulse [animation-delay:240ms]" />
          </div>
          <span className="text-xs tracking-widest text-[#525252] uppercase">{step.toUpperCase()}</span>
        </div>
        <p className="text-sm text-[#a3a3a3] leading-tight">{message}</p>
      </div>
    </div>
  )
}
