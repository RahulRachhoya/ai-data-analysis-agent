'use client'

import dynamic from 'next/dynamic'
import type { PlotData } from '@/types'

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

interface PlotViewerProps {
  plots: PlotData[]
}

export function PlotViewer({ plots }: PlotViewerProps) {
  if (!plots.length) return null

  return (
    <div className="space-y-4 my-4">
      {plots.map((plot, i) => (
        <div
          key={i}
          className="glass-card p-4 animate-slide-up overflow-hidden"
        >
          {plot.type === 'matplotlib' && plot.image && (
            <div className="flex items-center justify-center bg-white rounded-lg p-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={plot.image}
                alt={`Analysis plot ${i + 1}`}
                className="max-w-full h-auto rounded-lg shadow-sm"
              />
            </div>
          )}
          {plot.type === 'plotly' && plot.figure && (
            <div className="flex items-center justify-center">
              <Plot
                data={plot.figure.data as Plotly.Data[]}
                layout={{
                  ...(plot.figure.layout as Partial<Plotly.Layout>),
                  autosize: true,
                  margin: { l: 50, r: 30, t: 40, b: 50 },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                }}
                config={{ responsive: true, displayModeBar: false }}
                useResizeHandler
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
