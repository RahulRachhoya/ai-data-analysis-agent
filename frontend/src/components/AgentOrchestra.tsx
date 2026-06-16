'use client'

import { motion, useReducedMotion } from 'framer-motion'
import { Users } from 'lucide-react'

interface AgentOrchestraProps {
  statuses: Record<string, string>
  currentAgent?: string | null
  isStreaming?: boolean
}

const AGENT_LABELS: Record<string, string> = {
  supervisor: 'Supervisor',
  profiler: 'Profiler',
  planner: 'Planner',
  coder: 'Coder',
  executor: 'Executor',
  critic: 'Critic',
  suggester: 'Suggester',
  presenter: 'Presenter',
}

const isActiveStatus = (status: string): boolean => {
  const s = status.toLowerCase()
  return s.includes('active') || s.includes('orchestrat') || s.includes('execut') || s.includes('think') || s.includes('plan') || s.includes('profil') || s.includes('start')
}

export function AgentOrchestra({ statuses, currentAgent, isStreaming }: AgentOrchestraProps) {
  const reduceMotion = useReducedMotion()
  const entries = Object.keys(statuses).length > 0 
    ? Object.entries(statuses) 
    : [['supervisor', 'orchestrating']]

  return (
    <div className="professional-card p-1.5 rounded-[2rem] border border-[#262626]">
      <div className="bg-[#121212] rounded-[calc(2rem-0.375rem)] px-4 py-3">
        <div className="flex items-center gap-2 mb-2.5">
          <div className="w-5 h-5 rounded-full bg-white/5 flex items-center justify-center">
            <Users className="w-3 h-3 text-[#a3a3a3]" />
          </div>
          <div className="text-[10px] uppercase tracking-[0.14em] text-[#525252] font-medium">Live Agent Orchestra</div>
          {isStreaming && (
            <div className="ml-auto text-[10px] text-[#737373] tracking-widest">STREAMING</div>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          {entries.map(([agent, status]) => {
            const label = AGENT_LABELS[agent] || agent.charAt(0).toUpperCase() + agent.slice(1)
            const active = isActiveStatus(String(status)) || currentAgent === agent
            const isCurrent = currentAgent === agent

            return (
              <div
                key={agent}
                className={`group inline-flex items-center gap-1.5 rounded-xl border px-2.5 py-1 text-xs transition-all duration-200 ${isCurrent ? 'border-[#f4f4f5]/60 bg-[#1a1a1a]' : 'border-[#262626] bg-[#171717]'} hover:border-[#3f3f46]`}
              >
                <div className="relative flex items-center justify-center w-2 h-2">
                  <motion.div
                    className={`rounded-full ${active ? 'bg-[#f4f4f5]' : 'bg-[#525252]'} w-1.5 h-1.5`}
                    animate={reduceMotion || !active ? { scale: 1, opacity: 0.85 } : { scale: [1, 1.25, 1], opacity: [0.7, 1, 0.7] }}
                    transition={reduceMotion || !active ? { duration: 0.2 } : { duration: 1.6, repeat: Infinity, ease: [0.32, 0.72, 0, 1] }}
                  />
                  {active && !reduceMotion && (
                    <motion.div
                      className="absolute inset-[-2px] rounded-full border border-[#f4f4f5]/40"
                      animate={{ scale: [1, 1.6], opacity: [0.5, 0] }}
                      transition={{ duration: 1.6, repeat: Infinity, ease: [0.32, 0.72, 0, 1] }}
                    />
                  )}
                </div>
                <span className={`font-medium tracking-[-0.01em] ${isCurrent ? 'text-[#fafafa]' : 'text-[#a3a3a3] group-hover:text-[#d1d1d6]'}`}>
                  {label}
                </span>
                <span className="text-[#525252] text-[10px] tabular-nums ml-0.5">{String(status).slice(0, 12)}</span>
              </div>
            )
          })}
        </div>

        {currentAgent && (
          <div className="mt-2 text-[10px] text-[#525252] tracking-[0.02em]">
            Current: <span className="text-[#a3a3a3] font-medium">{AGENT_LABELS[currentAgent] || currentAgent}</span>
          </div>
        )}
      </div>
    </div>
  )
}
