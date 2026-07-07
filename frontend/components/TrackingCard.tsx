'use client'

import { useState, useEffect } from 'react'

interface SendLog {
  id: string
  sent_at: string
  template_name: string
  recipients_count: number
  status: string
}

interface TrackingStats {
  sent: number
  delivered: number
  read: number
}

export default function TrackingCard() {
  const [stats, setStats] = useState<TrackingStats>({
    sent: 0,
    delivered: 0,
    read: 0,
  })
  const [logs, setLogs] = useState<SendLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTrackingData()
    const interval = setInterval(fetchTrackingData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchTrackingData = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/logs`
      )
      if (response.ok) {
        const data = await response.json()
        setStats(data.stats || { sent: 0, delivered: 0, read: 0 })
        setLogs(data.logs || [])
      }
    } catch (error) {
      console.error('Failed to fetch tracking data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExportLog = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/logs/export`
      )
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `laceni-logs-${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Failed to export logs:', error)
    }
  }

  return (
    <div className="track-frame">
      <div className="track-inner">
        <div className="track-head">
          <h3 className="card-title">Tracking</h3>
          <button className="btn btn-ghost" onClick={handleExportLog}>
            Export log
          </button>
        </div>

        <div className="stat-grid">
          <div className="stat-tile accent">
            <div className="stat-num">{stats.sent}</div>
            <div className="stat-label">Messages sent</div>
          </div>
          <div className="stat-tile">
            <div className="stat-num">{stats.delivered}</div>
            <div className="stat-label">Delivered</div>
          </div>
          <div className="stat-tile">
            <div className="stat-num">{stats.read}</div>
            <div className="stat-label">Read</div>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Sent at</th>
              <th>Template</th>
              <th>Recipients</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr className="log-empty-row">
                <td colSpan={4}>
                  No messages sent yet. Once you send a campaign, each send will
                  appear here with delivery and read status.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.sent_at).toLocaleString()}</td>
                  <td>{log.template_name}</td>
                  <td>{log.recipients_count}</td>
                  <td>{log.status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
