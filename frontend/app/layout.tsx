import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Lāceni — WhatsApp Sūtne',
  description: 'WhatsApp message campaign manager for Lāceni',
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
