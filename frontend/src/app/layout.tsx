import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Aether • Professional Agentic Data Analysis',
  description: 'Enterprise-grade autonomous data analysis. Secure agentic Python execution in the cloud. Upload datasets, ask natural language questions, receive precise insights with beautiful visualizations.',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0a0a0a] text-[#fafafa] antialiased">
        {children}
      </body>
    </html>
  )
}
