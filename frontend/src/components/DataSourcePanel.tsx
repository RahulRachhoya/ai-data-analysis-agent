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
      const res = await fetch(`${API_BASE}/api/data/upload`, {
        method: 'POST',
        body: formData,
      })
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
        body: JSON.stringify({
          url: apiUrl.trim(),
          method: apiMethod,
          headers,
          body,
          response_path: apiResponsePath.trim() || undefined,
        }),
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
    { key: 'upload', label: 'Upload File', icon: Upload },
    { key: 'url', label: 'From URL', icon: Link },
    { key: 'api', label: 'From API', icon: Globe },
  ]

  if (dataset) {
    return (
      <div className="glass-card p-4 animate-fade-in">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="font-medium text-sm text-gray-900">{dataset.filename}</span>
          </div>
          <button
            onClick={() => { setDataset(null); setError(null) }}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            title="Remove dataset"
          >
            <XCircle className="w-4 h-4" />
          </button>
        </div>
        <div className="text-xs text-gray-500 space-y-1">
          <p>{dataset.row_count.toLocaleString()} rows · {dataset.columns.length} columns</p>
          <p className="truncate">{dataset.columns.join(', ')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="glass-card p-4 animate-fade-in">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Import Data</h3>

      {/* Mode Tabs */}
      <div className="flex gap-1 mb-4 p-1 bg-gray-100 rounded-lg">
        {modes.map(m => {
          const Icon = m.icon
          return (
            <button
              key={m.key}
              onClick={() => setMode(m.key)}
              className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                mode === m.key
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {m.label}
            </button>
          )
        })}
      </div>

      {/* Upload Mode */}
      {mode === 'upload' && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          {isDragActive ? (
            <p className="text-sm text-primary-600 font-medium">Drop your file here</p>
          ) : (
            <>
              <p className="text-sm text-gray-600 font-medium">Drop CSV or JSON here</p>
              <p className="text-xs text-gray-400 mt-1">or click to browse</p>
            </>
          )}
        </div>
      )}

      {/* URL Mode */}
      {mode === 'url' && (
        <div className="space-y-3">
          <div className="flex gap-2">
            <input
              type="url"
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://example.com/data.csv"
              className="input-field flex-1"
            />
            <button onClick={handleUrlImport} disabled={loading || !url.trim()} className="btn-primary">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Fetch'}
            </button>
          </div>
        </div>
      )}

      {/* API Mode */}
      {mode === 'api' && (
        <div className="space-y-3">
          <div className="flex gap-2">
            <select
              value={apiMethod}
              onChange={e => setApiMethod(e.target.value)}
              className="input-field w-20 shrink-0"
            >
              <option>GET</option>
              <option>POST</option>
            </select>
            <input
              type="url"
              value={apiUrl}
              onChange={e => setApiUrl(e.target.value)}
              placeholder="https://api.example.com/data"
              className="input-field flex-1"
            />
          </div>
          <input
            type="text"
            value={apiResponsePath}
            onChange={e => setApiResponsePath(e.target.value)}
            placeholder="Response path (e.g., data.results)"
            className="input-field"
          />
          <textarea
            value={apiHeaders}
            onChange={e => setApiHeaders(e.target.value)}
            placeholder="Headers (one per line: Key: Value)"
            className="input-field text-xs"
            rows={2}
          />
          <textarea
            value={apiBody}
            onChange={e => setApiBody(e.target.value)}
            placeholder='JSON body (for POST): {"key": "value"}'
            className="input-field text-xs font-mono"
            rows={3}
          />
          <button onClick={handleApiImport} disabled={loading || !apiUrl.trim()} className="btn-primary w-full">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Fetch from API'}
          </button>
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-2 mt-3 text-sm text-gray-500">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading dataset...
        </div>
      )}
      {error && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600">
          {error}
        </div>
      )}
    </div>
  )
}
