'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Loader2, User, Bot } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { Message, PlotData, StepType } from '@/types'
import { useSSE } from '@/hooks/useSSE'
import { CodeBlock } from './CodeBlock'
import { PlotViewer } from './PlotViewer'
import { AgentThinking } from './AgentThinking'
import { AgentOrchestra } from './AgentOrchestra'
import { SuggestionChips } from './SuggestionChips'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ChatInterfaceProps {
  datasetId: string | null
  onError: (error: string) => void
}

export function ChatInterface({ datasetId, onError }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [currentStep, setCurrentStep] = useState<{ step: StepType; message: string } | null>(null)
  const [agentStatuses, setAgentStatuses] = useState<Record<string, string>>({})
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [currentPlan, setCurrentPlan] = useState<string | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { connect, disconnect, isStreaming } = useSSE()

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
    setAgentStatuses({})
    setSuggestions([])
    setCurrentAgent(null)
    setCurrentPlan(null)
    pendingCodeRef.current = null
    pendingPlotsRef.current = []

    connect(
      `${API_BASE}/api/agent/query`,
      { question: questionText, dataset_id: datasetId },
      {
        onThinking: (step, message) => setCurrentStep({ step, message }),
        onCode: (code) => { pendingCodeRef.current = code },
        onPlot: (plot) => { pendingPlotsRef.current = [...pendingPlotsRef.current, plot] },
        onMessage: (content) => {
          setCurrentStep(null)
          const assistantMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content,
            code: pendingCodeRef.current || undefined,
            plots: pendingPlotsRef.current.length > 0 ? pendingPlotsRef.current : undefined,
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
        onDone: () => setCurrentStep(null),
        onPlan: (plan) => setCurrentPlan(plan),
        onSuggestions: (sugs) => setSuggestions(sugs),
        onAgentStatus: (statuses, current) => {
          if (statuses && Object.keys(statuses).length > 0) setAgentStatuses(statuses)
          if (current) setCurrentAgent(current)
        },
        onHeartbeat: (data) => {
          const hbStatuses = (data?.agent_statuses as Record<string, string>) || {}
          if (hbStatuses && Object.keys(hbStatuses).length > 0) {
            setAgentStatuses(prev => ({ ...prev, ...hbStatuses }))
          }
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

  const submitQuestion = (questionText: string) => {
    if (!questionText.trim() || !datasetId || isStreaming) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: questionText.trim(),
      timestamp: new Date(),
    }
    addMessage(userMessage)
    setInput('')
    setCurrentStep(null)
    setAgentStatuses({})
    setSuggestions([])
    setCurrentAgent(null)
    setCurrentPlan(null)
    pendingCodeRef.current = null
    pendingPlotsRef.current = []

    connect(
      `${API_BASE}/api/agent/query`,
      { question: questionText.trim(), dataset_id: datasetId },
      {
        onThinking: (step, message) => setCurrentStep({ step, message }),
        onCode: (code) => { pendingCodeRef.current = code },
        onPlot: (plot) => { pendingPlotsRef.current = [...pendingPlotsRef.current, plot] },
        onMessage: (content) => {
          setCurrentStep(null)
          const assistantMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content,
            code: pendingCodeRef.current || undefined,
            plots: pendingPlotsRef.current.length > 0 ? pendingPlotsRef.current : undefined,
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
        onDone: () => setCurrentStep(null),
        onPlan: (plan) => setCurrentPlan(plan),
        onSuggestions: (sugs) => setSuggestions(sugs),
        onAgentStatus: (statuses, current) => {
          if (statuses && Object.keys(statuses).length > 0) setAgentStatuses(statuses)
          if (current) setCurrentAgent(current)
        },
        onHeartbeat: (data) => {
          const hbStatuses = (data?.agent_statuses as Record<string, string>) || {}
          if (hbStatuses && Object.keys(hbStatuses).length > 0) {
            setAgentStatuses(prev => ({ ...prev, ...hbStatuses }))
          }
        },
      }
    )
  }

  const handleSuggestionSelect = (suggestion: string) => {
    submitQuestion(suggestion)
  }

  return (
    <div className="flex flex-col h-full bg-[#0a0a0a]">
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {(Object.keys(agentStatuses).length > 0 || isStreaming) && (
          <div className="mb-2">
            <AgentOrchestra
              statuses={agentStatuses}
              currentAgent={currentAgent}
              isStreaming={isStreaming}
            />
          </div>
        )}

        {currentPlan && (
          <div className="mb-2 px-1 text-[13px] text-[#a3a3a3] leading-snug border-l-2 border-[#262626] pl-3">
            <span className="uppercase tracking-[0.1em] text-[10px] text-[#525252]">Plan</span>
            <div className="mt-0.5">{currentPlan}</div>
          </div>
        )}

        {messages.length === 0 && !isStreaming && !Object.keys(agentStatuses).length && (
          <div className="h-full flex flex-col items-center justify-center text-center text-[#525252]">
            <Bot className="w-9 h-9 mb-3 opacity-40" />
            <div className="text-sm">Ask a precise question about your data.</div>
            <div className="text-[11px] mt-1 max-w-[260px]">The agent will plan, write secure Python, execute in isolation, and return rich visualizations + insights.</div>
          </div>
        )}

        {messages.map(msg => (
          <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded bg-white/5 flex items-center justify-center shrink-0 mt-1">
                <Bot className="w-4 h-4 text-[#a3a3a3]" />
              </div>
            )}
            <div className={`max-w-[78%] ${msg.role === 'user' ? 'text-right' : ''}`}>
              <div className={`message-bubble ${msg.role === 'user' ? 'bg-white text-black' : 'bg-[#171717] border border-[#262626]'}`}>
                <ReactMarkdown
                  components={{
                    code({ className, children, ...props }) {
                      const isInline = !className
                      return isInline ? <code className="font-mono text-xs bg-black/40 px-1 py-px rounded" {...props}>{children}</code> :
                        <CodeBlock code={String(children).replace(/\n$/, '')} />
                    },
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>

              {msg.code && <div className="mt-2"><CodeBlock code={msg.code} /></div>}
              {msg.plots && msg.plots.length > 0 && <PlotViewer plots={msg.plots} />}
            </div>
            {msg.role === 'user' && <div className="w-7 h-7 rounded bg-white/5 flex items-center justify-center shrink-0 mt-1"><User className="w-4 h-4 text-[#a3a3a3]" /></div>}
          </div>
        ))}

        {isStreaming && currentStep && <AgentThinking step={currentStep.step} message={currentStep.message} />}
        <div ref={chatEndRef} />
      </div>

      <div className="border-t border-[#1f1f1f] p-4 bg-[#0a0a0a]">
        <div className="max-w-3xl mx-auto">
          <SuggestionChips
            suggestions={suggestions}
            onSelect={handleSuggestionSelect}
            disabled={!datasetId || isStreaming}
          />
          <div className="flex gap-3 items-end">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={datasetId ? "Ask a focused question..." : "Load a dataset to begin"}
              disabled={!datasetId || isStreaming}
              className="input-professional resize-none flex-1 min-h-[48px] max-h-[140px] py-3.5"
              rows={1}
            />
            <button
              onClick={handleSubmit}
              disabled={!input.trim() || !datasetId || isStreaming}
              className="btn-primary h-[48px] w-[48px] p-0 flex items-center justify-center rounded-2xl"
            >
              {isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
