'use client'

import { useState } from 'react'
import { Bot, Database, AlertCircle, X, ArrowRight } from 'lucide-react'
import { DataSourcePanel } from '@/components/DataSourcePanel'
import { ChatInterface } from '@/components/ChatInterface'
import type { DatasetInfo } from '@/types'

export default function AetherProfessional() {
  const [dataset, setDataset] = useState<DatasetInfo | null>(null)
  const [error, setError] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#fafafa] flex flex-col">
      {/* Professional Top Bar */}
      <header className="border-b border-[#1f1f1f] bg-[#0a0a0a]/95 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
              <Bot className="w-4.5 h-4.5 text-black" />
            </div>
            <div>
              <div className="font-semibold tracking-[-0.025em] text-lg">Aether</div>
              <div className="text-[10px] text-[#525252] -mt-1">DATA INTELLIGENCE</div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-sm">
            <div className="px-3 py-1 rounded-full bg-[#111] border border-[#222] text-[#a3a3a3] text-xs font-medium tracking-widest">
              SECURE AGENTIC ANALYSIS
            </div>
            {dataset && (
              <div className="flex items-center gap-2 px-4 py-1.5 bg-[#111] border border-[#222] rounded-2xl text-xs">
                <Database className="w-3.5 h-3.5" />
                <span className="font-medium truncate max-w-[220px]">{dataset.filename}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {!dataset ? (
        /* Professional Landing / Onboarding */ 
        <div className="flex-1 flex items-center justify-center px-6 pt-10 pb-20">
          <div className="max-w-3xl text-center">
            <div className="inline-block px-4 py-1 text-xs tracking-[3px] font-medium border border-[#333] rounded-full mb-6 text-[#737373]">
              PROFESSIONAL EDITION
            </div>

            <h1 className="text-6xl md:text-7xl font-semibold tracking-tighter leading-[.96] mb-4">
              Precision data<br />analysis.<br />
              <span className="text-[#a3a3a3]">Autonomous.</span>
            </h1>

            <p className="max-w-md mx-auto text-xl text-[#a3a3a3] tracking-[-0.015em] mb-10">
              Upload your data. Ask anything. Get production-grade insights with visualizations — powered by secure agentic execution.
            </p>

            {/* Elegant Data Import */}
            <div className="max-w-2xl mx-auto">
              <div className="professional-card p-9">
                <div className="mb-5 text-left">
                  <div className="text-xs uppercase tracking-widest text-[#525252] mb-1.5">GET STARTED</div>
                  <div className="text-2xl font-medium tracking-tight">Import your dataset</div>
                </div>
                <DataSourcePanel onDatasetLoaded={setDataset} />
              </div>
            </div>

            <div className="mt-8 text-[10px] text-[#525252] tracking-widest">
              CSV · JSON · URL · API  ·  End-to-end encrypted execution in isolated sandboxes
            </div>
          </div>
        </div>
      ) : (
        /* Professional Workspace */ 
        <div className="flex-1 max-w-7xl mx-auto w-full px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">
            {/* Left Data Panel */}
            <div className="lg:col-span-3">
              <div className="sticky top-20">
                <div className="section-header mb-2.5">DATASET</div>
                <div className="professional-card p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="font-medium tracking-tight text-lg leading-none mb-1.5">{dataset.filename}</div>
                      <div className="text-xs text-[#737373]">
                        {dataset.row_count.toLocaleString()} rows · {dataset.columns.length} columns
                      </div>
                    </div>
                    <button 
                      onClick={() => setDataset(null)}
                      className="text-xs px-3 py-1 rounded-lg border border-[#333] hover:bg-[#1a1a1a] text-[#a3a3a3] hover:text-white transition-colors"
                    >
                      Change
                    </button>
                  </div>

                  <div className="text-[13px] text-[#a3a3a3] leading-snug">
                    {dataset.columns.slice(0, 6).join(', ')}{dataset.columns.length > 6 && ' …'}
                  </div>
                </div>

                <div className="mt-6">
                  <div className="section-header mb-3">NEW ANALYSIS</div>
                  <DataSourcePanel onDatasetLoaded={setDataset} />
                </div>
              </div>
            </div>

            {/* Main Chat & Results */}
            <div className="lg:col-span-9 min-h-[620px]">
              <div className="professional-card h-full flex flex-col overflow-hidden">
                <div className="px-8 pt-6 pb-3 border-b border-[#222]">
                  <div className="font-medium tracking-tight">Analysis Workspace</div>
                  <div className="text-xs text-[#525252]">Ask natural language questions. The agent writes, executes, and explains.</div>
                </div>

                <div className="flex-1 min-h-0">
                  <ChatInterface 
                    datasetId={dataset?.dataset_id || null} 
                    onError={setError} 
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Elegant Error Toast */}
      {error && (
        <div className="fixed bottom-8 right-8 max-w-sm animate-slide-up z-[100]">
          <div className="professional-card p-5 flex items-start gap-4 border-red-900/40">
            <AlertCircle className="w-5 h-5 mt-0.5 text-red-400 shrink-0" />
            <div className="flex-1 text-sm">
              <div className="font-medium mb-px">Something went wrong</div>
              <div className="text-[#a3a3a3]">{error}</div>
            </div>
            <button onClick={() => setError(null)} className="text-[#525252] hover:text-white p-1 -mr-1">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      <footer className="mt-auto border-t border-[#1f1f1f] py-4">
        <div className="max-w-7xl mx-auto px-8 text-[10px] text-[#525252] flex justify-between">
          <div>Powered by LangGraph · E2B Secure Sandbox</div>
          <div>Professional • Secure • Precise</div>
        </div>
      </footer>
    </div>
  )
}
