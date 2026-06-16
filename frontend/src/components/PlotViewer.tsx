'use client'

import dynamic from 'next/dynamic'
import type { PlotData } from '@/types'

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

interface PlotViewerProps {
  plots: PlotData[]
}

export function PlotViewer({ plots }: PlotViewerProps) {
  if (!plots.length) return null

  return (
    <div className="space-y-4 mt-4">
      {plots.map((plot, i) => (
        <div key={i} className="professional-card p-5">
          {plot.type === 'matplotlib' && plot.image && (
            <div className="flex justify-center bg-[#0a0a0a] rounded-xl p-3 border border-[#1f1f1f]">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={plot.image} alt={`Plot ${i + 1}`} className="max-w-full h-auto rounded" />
            </div>
          )}
          {plot.type === 'plotly' && plot.figure && (
            <div>
              <Plot
                data={plot.figure.data as Plotly.Data[]}
                layout={{
                  ...(plot.figure.layout as Partial<Plotly.Layout>),
                  autosize: true,
                  paper_bgcolor: '#0a0a0a',
                  plot_bgcolor: '#111',
                  font: { color: '#a3a3a3', size: 11 },
                  margin: { l: 45, r: 25, t: 35, b: 40 },
                }}
                config={{ responsive: true, displayModeBar: false }}
                useResizeHandler
                style={{ width: '100%', height: 380 }}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
