import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Agentic Data Analysis Sandbox',
  description: 'AI-powered data analysis with LangGraph agents. Upload data, ask questions, get insights with visualizations.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
