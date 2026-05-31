'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Loader2, User, Bot } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { Message, PlotData, StepType } from '@/types'
import { useSSE } from '@/hooks/useSSE'
import { CodeBlock } from './CodeBlock'
import { PlotViewer } from './PlotViewer'
import { AgentThinking } from './AgentThinking'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ChatInterfaceProps {
  datasetId: string | null
  onError: (error: string) => void
}

export function ChatInterface({ datasetId, onError }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [currentStep, setCurrentStep] = useState<{ step: StepType; message: string } | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { connect, disconnect, isStreaming } = useSSE()

  // Use refs to avoid stale closure issues in SSE callbacks
  const pendingCodeRef = useRef<string | null>(null)
  const pendingPlotsRef = useRef<PlotData[]>([])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentStep])

  const addMessage = useCallback((msg: Message) => {
    setMessages(prev => [...prev, msg])
  }, [])

  const handleSubmit = async () => {
    if (!input.trim() || !datasetId || isStreaming) return

    const questionText = input.trim()

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: questionText,
      timestamp: new Date(),
    }
    addMessage(userMessage)
    setInput('')
    setCurrentStep(null)
    pendingCodeRef.current = null
    pendingPlotsRef.current = []

    connect(
      `${API_BASE}/api/agent/query`,
      { question: questionText, dataset_id: datasetId },
      {
        onThinking: (step, message) => {
          setCurrentStep({ step, message })
        },
        onCode: (code) => {
          pendingCodeRef.current = code
          setCurrentStep(prev => prev) // Force re-render to show thinking
        },
        onPlot: (plot) => {
          pendingPlotsRef.current = [...pendingPlotsRef.current, plot]
          setCurrentStep(prev => prev)
        },
        onStdout: () => {
          // stdout is captured but not displayed as a separate message
        },
        onMessage: (content) => {
          setCurrentStep(null)
          const code = pendingCodeRef.current
          const plots = pendingPlotsRef.current
          const assistantMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content,
            code: code || undefined,
            plots: plots.length > 0 ? plots : undefined,
            timestamp: new Date(),
          }
          addMessage(assistantMsg)
          pendingCodeRef.current = null
          pendingPlotsRef.current = []
        },
        onError: (message) => {
          setCurrentStep(null)
          onError(message)
        },
        onDone: () => {
          setCurrentStep(null)
        },
      }
    )
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400 space-y-2">
            <Bot className="w-12 h-12" />
            <p className="text-sm font-medium">Ask a question about your data</p>
            <p className="text-xs max-w-xs">
              The agent will analyze your dataset, write code, generate visualizations, and explain the results.
            </p>
          </div>
        )}

        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 px-4 py-3 rounded-xl animate-slide-up ${
              msg.role === 'user'
                ? 'bg-primary-50 border border-primary-100 ml-12'
                : 'glass-card mr-12'
            }`}
          >
            <div className={`mt-0.5 shrink-0 ${
              msg.role === 'user' ? 'text-primary-600' : 'text-gray-500'
            }`}>
              {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm leading-relaxed">
                <ReactMarkdown
                  components={{
                    code({ className, children, ...props }) {
                      const isInline = !className
                      return isInline ? (
                        <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs font-mono text-primary-700" {...props}>
                          {children}
                        </code>
                      ) : (
                        <CodeBlock code={String(children).replace(/\n$/, '')} />
                      )
                    },
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
              {msg.code && <CodeBlock code={msg.code} />}
              {msg.plots && msg.plots.length > 0 && <PlotViewer plots={msg.plots} />}
            </div>
          </div>
        ))}

        {/* Streaming state indicators */}
        {isStreaming && currentStep && (
          <AgentThinking step={currentStep.step} message={currentStep.message} />
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={datasetId ? "Ask a question about your data..." : "Import a dataset first..."}
              disabled={!datasetId || isStreaming}
              className="input-field resize-none pr-12 py-3 min-h-[44px] max-h-[120px]"
              rows={1}
            />
          </div>
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || !datasetId || isStreaming}
            className="btn-primary h-[44px] w-[44px] p-0 flex items-center justify-center shrink-0"
          >
            {isStreaming ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
