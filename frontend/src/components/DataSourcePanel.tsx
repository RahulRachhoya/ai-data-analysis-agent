'use client'

import { useState, useCallback } from 'react'
import { Upload, Link, Globe, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import type { DataSourceMode, DatasetInfo } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface DataSourcePanelProps {
  onDatasetLoaded: (info: DatasetInfo) => void
}

export function DataSourcePanel({ onDatasetLoaded }: DataSourcePanelProps) {
  const [mode, setMode] = useState<DataSourceMode>('upload')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dataset, setDataset] = useState<DatasetInfo | null>(null)

  const [url, setUrl] = useState('')
  const [apiUrl, setApiUrl] = useState('')
  const [apiMethod, setApiMethod] = useState('GET')
  const [apiHeaders, setApiHeaders] = useState('')
  const [apiBody, setApiBody] = useState('')
  const [apiResponsePath, setApiResponsePath] = useState('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setLoading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API_BASE}/api/data/upload`, { method: 'POST', body: formData })
      if (!res.ok) throw new Error((await res.text()) || 'Upload failed')
      const info = await res.json()
      setDataset(info)
      onDatasetLoaded(info)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }, [onDatasetLoaded])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'application/json': ['.json'] },
    maxFiles: 1,
  })

  const handleUrlImport = async () => {
    if (!url.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/data/url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })
      if (!res.ok) throw new Error((await res.text()) || 'Import failed')
      const info = await res.json()
      setDataset(info)
      onDatasetLoaded(info)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'URL import failed')
    } finally {
      setLoading(false)
    }
  }

  const handleApiImport = async () => {
    if (!apiUrl.trim()) return
    setLoading(true)
    setError(null)
    try {
      let headers: Record<string, string> | undefined
      if (apiHeaders.trim()) {
        headers = Object.fromEntries(
          apiHeaders.split('\n').map(l => l.split(':').map(s => s.trim())).filter(([k]) => k)
        )
      }
      let body: Record<string, unknown> | undefined
      if (apiBody.trim()) {
        body = JSON.parse(apiBody)
      }

      const res = await fetch(`${API_BASE}/api/data/api`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: apiUrl.trim(), method: apiMethod, headers, body, response_path: apiResponsePath.trim() || undefined }),
      })
      if (!res.ok) throw new Error((await res.text()) || 'API import failed')
      const info = await res.json()
      setDataset(info)
      onDatasetLoaded(info)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'API import failed')
    } finally {
      setLoading(false)
    }
  }

  const modes: { key: DataSourceMode; label: string; icon: typeof Upload }[] = [
    { key: 'upload', label: 'File Upload', icon: Upload },
    { key: 'url', label: 'Public URL', icon: Link },
    { key: 'api', label: 'REST API', icon: Globe },
  ]

  if (dataset) {
    return (
      <div className="professional-card p-6 animate-fade-in">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <span className="font-medium text-base tracking-tight">{dataset.filename}</span>
          </div>
          <button onClick={() => { setDataset(null); setError(null) }} className="text-[#525252] hover:text-white transition-colors">
            <XCircle className="w-4 h-4" />
          </button>
        </div>
        <div className="text-xs text-[#737373] space-y-px">
          <div>{dataset.row_count.toLocaleString()} rows · {dataset.columns.length} columns</div>
          <div className="truncate pt-1.5 border-t border-[#222] mt-3">{dataset.columns.join(', ')}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="professional-card p-6 animate-fade-in">
      <div className="flex gap-1 mb-6 p-1 bg-[#0a0a0a] border border-[#222] rounded-2xl">
        {modes.map(m => {
          const Icon = m.icon
          return (
            <button
              key={m.key}
              onClick={() => setMode(m.key)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 text-xs font-medium rounded-[14px] transition-all ${mode === m.key ? 'bg-[#1f1f1f] text-white shadow' : 'text-[#a3a3a3] hover:text-[#d4d4d8]'}`}
            >
              <Icon className="w-3.5 h-3.5" />
              {m.label}
            </button>
          )
        })}
      </div>

      {mode === 'upload' && (
        <div
          {...getRootProps()}
          className={`border border-dashed rounded-2xl p-9 text-center cursor-pointer transition-all border-[#333] hover:border-[#555] ${isDragActive ? 'border-[#666] bg-[#111]' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="mx-auto w-10 h-10 rounded-2xl bg-[#1a1a1a] flex items-center justify-center mb-4">
            <Upload className="w-5 h-5 text-[#737373]" />
          </div>
          {isDragActive ? (
            <p className="font-medium text-sm">Release to upload</p>
          ) : (
            <>
              <p className="font-medium text-sm mb-1 tracking-tight">Drop CSV or JSON file</p>
              <p className="text-xs text-[#525252]">or click to select</p>
            </>
          )}
        </div>
      )}

      {mode === 'url' && (
        <div className="space-y-3">
          <input type="url" value={url} onChange={e => setUrl(e.target.value)} placeholder="https://example.com/dataset.csv" className="input-professional" />
          <button onClick={handleUrlImport} disabled={loading || !url.trim()} className="btn-primary w-full">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Fetch Dataset <ArrowRight className="w-4 h-4" /></> }
          </button>
        </div>
      )}

      {mode === 'api' && (
        <div className="space-y-3">
          <div className="grid grid-cols-[72px,1fr] gap-2">
            <select value={apiMethod} onChange={e => setApiMethod(e.target.value)} className="input-professional">
              <option>GET</option>
              <option>POST</option>
            </select>
            <input type="url" value={apiUrl} onChange={e => setApiUrl(e.target.value)} placeholder="https://api.example.com/v1/data" className="input-professional" />
          </div>
          <input type="text" value={apiResponsePath} onChange={e => setApiResponsePath(e.target.value)} placeholder="JSON path (optional)" className="input-professional" />
          <textarea value={apiHeaders} onChange={e => setApiHeaders(e.target.value)} placeholder="Headers (Key: Value, one per line)" className="input-professional text-xs font-mono" rows={2} />
          <textarea value={apiBody} onChange={e => setApiBody(e.target.value)} placeholder='POST JSON body' className="input-professional text-xs font-mono" rows={2} />
          <button onClick={handleApiImport} disabled={loading || !apiUrl.trim()} className="btn-primary w-full">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Fetch from API'}
          </button>
        </div>
      )}

      {loading && <div className="text-xs text-[#737373] flex items-center gap-2 mt-4"><Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing securely…</div>}
      {error && <div className="mt-3 text-xs text-red-400 bg-red-950/30 border border-red-900 p-3 rounded-xl">{error}</div>}
    </div>
  )
}
