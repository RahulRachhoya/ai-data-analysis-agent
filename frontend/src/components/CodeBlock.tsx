'use client'

import { Terminal } from 'lucide-react'

interface CodeBlockProps {
  code: string
  language?: string
}

export function CodeBlock({ code, language = 'python' }: CodeBlockProps) {
  const handleCopy = () => {
    navigator.clipboard.writeText(code)
  }

  return (
    <div className="relative group rounded-lg overflow-hidden border border-gray-200 bg-[#1e1e2e] my-3 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#181825] border-b border-[#313244]">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-[#89b4fa]" />
          <span className="text-xs font-medium text-[#a6adc8]">{language}</span>
        </div>
        <button
          onClick={handleCopy}
          className="text-xs text-[#a6adc8] hover:text-white transition-colors px-2 py-1 rounded hover:bg-[#313244]"
        >
          Copy
        </button>
      </div>
      {/* Code */}
      <pre className="p-4 overflow-x-auto">
        <code className="text-sm leading-relaxed text-[#cdd6f4] font-mono whitespace-pre">
          {code}
        </code>
      </pre>
    </div>
  )
}
