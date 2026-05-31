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

const stepColors: Record<StepType, string> = {
  analyzing: 'text-blue-500',
  planning: 'text-purple-500',
  coding: 'text-emerald-500',
  executing: 'text-orange-500',
  fixing: 'text-red-500',
}

export function AgentThinking({ step, message }: AgentThinkingProps) {
  const Icon = stepIcons[step]

  return (
    <div className="flex items-start gap-3 px-4 py-3 animate-fade-in">
      <div className={`mt-0.5 ${stepColors[step]}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
        <p className="text-sm text-gray-600">{message}</p>
      </div>
    </div>
  )
}
