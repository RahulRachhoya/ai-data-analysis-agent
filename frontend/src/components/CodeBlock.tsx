'use client'

import { Terminal, Copy, Check } from 'lucide-react'
import { useState } from 'react'

interface CodeBlockProps {
  code: string
  language?: string
}

export function CodeBlock({ code, language = 'python' }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    })
  }

  return (
    <div className="code-block my-3 text-sm">
      <div className="flex items-center justify-between px-4 py-[9px] border-b border-[#1f1f1f] bg-[#111]">
        <div className="flex items-center gap-2 text-xs text-[#737373]">
          <Terminal className="w-3.5 h-3.5" />
          <span>{language}</span>
        </div>
        <button 
          onClick={handleCopy} 
          className="flex items-center gap-1.5 text-xs px-2 py-0.5 rounded hover:bg-[#1a1a1a] text-[#737373] hover:text-[#d4d4d8] transition-colors"
        >
          {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-[#d4d4d8] whitespace-pre leading-[1.55] tracking-[-0.01em]">
        <code>{code}</code>
      </pre>
    </div>
  )
}
