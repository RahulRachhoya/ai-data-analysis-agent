'use client'

import { useState } from 'react'
import { Bot, Database, AlertCircle, X } from 'lucide-react'
import { DataSourcePanel } from '@/components/DataSourcePanel'
import { ChatInterface } from '@/components/ChatInterface'
import type { DatasetInfo } from '@/types'

export default function Home() {
  const [dataset, setDataset] = useState<DatasetInfo | null>(null)
  const [error, setError] = useState<string | null>(null)

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-3 shrink-0">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center shadow-sm">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Agentic Data Analysis</h1>
              <p className="text-xs text-gray-500">Powered by LangGraph + E2B Sandbox</p>
            </div>
          </div>
          {dataset && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-lg">
              <Database className="w-3.5 h-3.5 text-green-600" />
              <span className="text-xs font-medium text-green-700 truncate max-w-[200px]">
                {dataset.filename}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex gap-4 p-4 max-w-7xl mx-auto w-full min-h-0">
        {/* Sidebar - Data Source */}
        <aside className="w-80 shrink-0 flex flex-col gap-4 overflow-y-auto">
          <DataSourcePanel onDatasetLoaded={setDataset} />
          
          {/* Tips */}
          <div className="glass-card p-4">
            <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-2">Tips</h3>
            <ul className="space-y-2 text-xs text-gray-500">
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                Upload CSV or JSON files
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                Ask specific questions about your data
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                The agent will write & execute Python code
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-500 mt-0.5">•</span>
                Results include charts and insights
              </li>
            </ul>
          </div>
        </aside>

        {/* Chat Area */}
        <main className="flex-1 glass-card flex flex-col min-h-0 overflow-hidden">
          <ChatInterface datasetId={dataset?.dataset_id || null} onError={setError} />
        </main>
      </div>

      {/* Error Toast */}
      {error && (
        <div className="fixed bottom-6 right-6 animate-slide-up z-50">
          <div className="flex items-start gap-3 bg-red-900/95 backdrop-blur-sm text-white px-5 py-4 rounded-xl shadow-xl border border-red-700/50 max-w-sm">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-red-400" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">Error</p>
              <p className="text-xs text-red-200 mt-1">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="shrink-0 text-red-300 hover:text-white transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
