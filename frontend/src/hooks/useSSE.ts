'use client'

import { useCallback, useRef, useState } from 'react'
import type { PlotData, StepType } from '@/types'

interface SSEHandlers {
  onThinking?: (step: StepType, message: string) => void
  onCode?: (code: string) => void
  onPlot?: (plot: PlotData) => void
  onStdout?: (text: string) => void
  onMessage?: (content: string) => void
  onError?: (message: string) => void
  onDone?: () => void
}

export function useSSE() {
  const [isConnected, setIsConnected] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const connect = useCallback(
    async (url: string, body: Record<string, unknown>, handlers: SSEHandlers) => {
      abortRef.current?.abort()
      const controller = new AbortController()
      abortRef.current = controller

      setIsConnected(true)
      setIsStreaming(true)

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
          signal: controller.signal,
        })

        if (!response.ok) {
          handlers.onError?.(`Server error: ${response.status}`)
          setIsStreaming(false)
          return
        }

        const reader = response.body?.getReader()
        if (!reader) {
          handlers.onError?.('No response body')
          setIsStreaming(false)
          return
        }

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          let currentEvent = ''
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim()
            } else if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim()
              try {
                const data = JSON.parse(dataStr)
                switch (currentEvent) {
                  case 'thinking':
                    handlers.onThinking?.(data.step as StepType, data.message as string)
                    break
                  case 'code':
                    handlers.onCode?.(data.code as string)
                    break
                  case 'plot':
                    handlers.onPlot?.(data as PlotData)
                    break
                  case 'stdout':
                    handlers.onStdout?.(data.text as string)
                    break
                  case 'message':
                    handlers.onMessage?.(data.content as string)
                    break
                  case 'error':
                    handlers.onError?.(data.message as string)
                    break
                  case 'done':
                    handlers.onDone?.()
                    break
                }
              } catch {
                // Ignore parse errors for incomplete chunks
              }
              currentEvent = ''
            }
          }
        }
      } catch (error: unknown) {
        if (error instanceof Error && error.name !== 'AbortError') {
          handlers.onError?.(error.message)
        }
      } finally {
        setIsStreaming(false)
        setIsConnected(false)
      }
    },
    []
  )

  const disconnect = useCallback(() => {
    abortRef.current?.abort()
    abortRef.current = null
    setIsConnected(false)
    setIsStreaming(false)
  }, [])

  return { connect, disconnect, isConnected, isStreaming }
}
