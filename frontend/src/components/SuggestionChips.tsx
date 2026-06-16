'use client'

import { motion, useReducedMotion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'

interface SuggestionChipsProps {
  suggestions: string[]
  onSelect: (suggestion: string) => void
  disabled?: boolean
}

export function SuggestionChips({ suggestions, onSelect, disabled }: SuggestionChipsProps) {
  const reduceMotion = useReducedMotion()
  if (!suggestions || suggestions.length === 0) return null

  return (
    <div className="mt-3 mb-1">
      <div className="text-[10px] uppercase tracking-[0.14em] text-[#525252] mb-1.5 px-1">Suggested next analyses</div>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, idx) => (
          <motion.button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(suggestion)}
            whileHover={reduceMotion || disabled ? {} : { scale: 1.005, y: -1 }}
            whileTap={reduceMotion || disabled ? {} : { scale: 0.985 }}
            transition={{ type: 'spring', stiffness: 280, damping: 22 }}
            className="group inline-flex items-center gap-1.5 rounded-2xl border border-[#262626] bg-[#171717] px-3.5 py-1.5 text-xs text-[#d1d1d6] hover:border-[#3f3f46] hover:bg-[#1f1f1f] active:bg-[#111] disabled:opacity-50 disabled:cursor-not-allowed transition-colors tracking-[-0.01em]"
          >
            <span className="max-w-[42ch] truncate text-left leading-snug">{suggestion}</span>
            <span className="ml-0.5 inline-flex h-4 w-4 items-center justify-center rounded-full border border-[#262626] text-[#737373] group-hover:border-[#3f3f46] group-hover:text-[#a3a3a3] transition-colors">
              <ArrowRight className="h-3 w-3" />
            </span>
          </motion.button>
        ))}
      </div>
    </div>
  )
}
