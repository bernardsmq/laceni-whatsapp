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
  total: number
  sent: number
  delivered: number
  read: number
}

interface DateRange {
  from: string
  to: string
}

export default function TrackingCard() {
  const [stats, setStats] = useState<TrackingStats>({
    total: 0,
    sent: 0,
    delivered: 0,
    read: 0,
  })
  const [logs, setLogs] = useState<SendLog[]>([])
  const [loading, setLoading] = useState(true)
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [dateRange, setDateRange] = useState<DateRange | null>(null)

  useEffect(() => {
    fetchTrackingData()
    const interval = setInterval(fetchTrackingData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [dateRange])

  const fetchTrackingData = async () => {
    try {
      const params = new URLSearchParams()
      if (dateRange) {
        params.append('date_from', dateRange.from)
        params.append('date_to', dateRange.to)
      }

      // Fetch analytics stats (sent/delivered/read counts from message_status)
      const statsResponse = await fetch(`/api/analytics/campaign-stats?${params}`)
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats({
          total: statsData.stats.total,
          sent: statsData.stats.sent,
          delivered: statsData.stats.delivered,
          read: statsData.stats.read,
        })
      }

      // Fetch message list
      const logsResponse = await fetch(`/api/analytics/all-messages?${params}`)
      if (logsResponse.ok) {
        const logsData = await logsResponse.json()
        // Map message_status format to SendLog format for display
        const formattedLogs = logsData.messages.map((msg: any) => ({
          id: msg.id,
          sent_at: msg.created_at,
          template_name: msg.template_id,
          recipients_count: 1,
          status: msg.status,
        }))
        setLogs(formattedLogs)
      }
    } catch (error) {
      console.error('Failed to fetch tracking data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExportLog = async () => {
    try {
      const response = await fetch('/api/logs/export')
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

  const handleSortByDate = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
  }

  const getSortedLogs = () => {
    const sorted = [...logs].sort((a, b) => {
      const dateA = new Date(a.sent_at).getTime()
      const dateB = new Date(b.sent_at).getTime()
      return sortOrder === 'asc' ? dateA - dateB : dateB - dateA
    })
    return sorted
  }

  const getToday = () => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    return {
      from: today.toISOString(),
      to: tomorrow.toISOString(),
    }
  }

  const getYesterday = () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    yesterday.setHours(0, 0, 0, 0)
    const today = new Date(yesterday)
    today.setDate(today.getDate() + 1)
    return {
      from: yesterday.toISOString(),
      to: today.toISOString(),
    }
  }

  const getPast7Days = () => {
    const to = new Date()
    to.setHours(23, 59, 59, 999)
    const from = new Date(to)
    from.setDate(from.getDate() - 6)
    from.setHours(0, 0, 0, 0)
    return {
      from: from.toISOString(),
      to: to.toISOString(),
    }
  }

  const handleDateFilter = (range: DateRange) => {
    setDateRange(range)
  }

  const handleClearFilter = () => {
    setDateRange(null)
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

        <div className="date-filter-container">
          <button
            className={`date-filter-btn ${dateRange === null ? 'active' : ''}`}
            onClick={handleClearFilter}
          >
            All time
          </button>
          <button
            className={`date-filter-btn ${dateRange && dateRange.from === getPast7Days().from ? 'active' : ''}`}
            onClick={() => handleDateFilter(getPast7Days())}
          >
            Past 7 days
          </button>
          <button
            className={`date-filter-btn ${dateRange && dateRange.from === getToday().from ? 'active' : ''}`}
            onClick={() => handleDateFilter(getToday())}
          >
            Today
          </button>
          <button
            className={`date-filter-btn ${dateRange && dateRange.from === getYesterday().from ? 'active' : ''}`}
            onClick={() => handleDateFilter(getYesterday())}
          >
            Yesterday
          </button>
        </div>

        <div className="stat-grid">
          <div className="stat-tile accent">
            <div className="stat-num">{stats.total}</div>
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
              <th
                style={{ cursor: 'pointer', userSelect: 'none' }}
                onClick={handleSortByDate}
                title="Click to sort"
              >
                Sent at {sortOrder === 'asc' ? '↑' : '↓'}
              </th>
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
              getSortedLogs().map((log) => (
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
