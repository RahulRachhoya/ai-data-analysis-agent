export interface DatasetInfo {
  dataset_id: string
  filename: string
  row_count: number
  columns: string[]
  dtypes?: Record<string, string>
  preview: Record<string, unknown>[]
  numeric_stats?: Record<string, NumericStats>
}

export interface NumericStats {
  min: number | null
  max: number | null
  mean: number | null
  median: number | null
}

export interface PlotData {
  type: 'matplotlib' | 'plotly'
  image?: string
  figure?: Record<string, unknown>
}

export interface SSEEvent {
  event: string
  data: Record<string, unknown>
}

export type StepType = 'analyzing' | 'planning' | 'coding' | 'executing' | 'fixing'

export interface AgentStep {
  step: StepType
  message: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  code?: string
  plots?: PlotData[]
  timestamp: Date
}

export type DataSourceMode = 'upload' | 'url' | 'api'

export interface DataSourceConfig {
  mode: DataSourceMode
  file?: File
  url?: string
  apiUrl?: string
  apiMethod?: string
  apiHeaders?: string
  apiBody?: string
  apiResponsePath?: string
}
