'use client'

import { useState, useEffect } from 'react'

interface Contact {
  id: string
  name: string
  phone: string
}

interface ContactsCardProps {
  connected: boolean
  onConnect?: () => void
}

export default function ContactsCard({ connected }: ContactsCardProps) {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [syncMessage, setSyncMessage] = useState('')

  useEffect(() => {
    fetchContacts()
  }, [])

  const fetchContacts = async () => {
    try {
      const response = await fetch('/api/contacts')
      if (response.ok) {
        const data = await response.json()
        setContacts(data.contacts || [])
      }
    } catch (error) {
      console.error('Failed to fetch contacts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSync = async () => {
    setSyncing(true)
    setSyncMessage('')

    try {
      const response = await fetch('/api/sync-contacts', { method: 'POST' })
      if (response.ok) {
        const data = await response.json()
        setSyncMessage(`✅ Synced ${data.synced} contacts from Google Sheet`)
        await fetchContacts()
      } else {
        setSyncMessage('❌ Sync failed - check your credentials')
      }
    } catch (error) {
      setSyncMessage('❌ Error syncing contacts')
      console.error(error)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <p className="card-eyebrow">Google Sheets</p>
          <h3 className="card-title">Contact list</h3>
        </div>
      </div>

      {syncMessage && (
        <div
          style={{
            padding: '12px',
            marginBottom: '12px',
            borderRadius: '8px',
            backgroundColor: syncMessage.includes('✅') ? '#e8ffe8' : '#ffe8e8',
            color: syncMessage.includes('✅') ? '#2e7d32' : '#c4482f',
            fontSize: '13px',
          }}
        >
          {syncMessage}
        </div>
      )}

      <div style={{ marginBottom: '12px', display: 'flex', gap: '8px', alignItems: 'center' }}>
        <button
          className="btn btn-primary"
          onClick={handleSync}
          disabled={syncing || loading}
          style={{ padding: '8px 12px', fontSize: '12px' }}
        >
          {syncing ? '⏳ Syncing...' : '🔄 Refresh'}
        </button>
        {contacts.length > 0 && (
          <span style={{ fontSize: '12px', color: '#8a8374' }}>
            {contacts.length} contact{contacts.length !== 1 ? 's' : ''} synced
          </span>
        )}
      </div>

      {syncMessage && (
        <div
          style={{
            padding: '12px',
            marginBottom: '12px',
            borderRadius: '8px',
            backgroundColor: syncMessage.includes('✅') ? '#e8ffe8' : '#ffe8e8',
            color: syncMessage.includes('✅') ? '#2e7d32' : '#c4482f',
            fontSize: '13px',
          }}
        >
          {syncMessage}
        </div>
      )}

      {loading ? (
        <div style={{ padding: '16px', textAlign: 'center', color: '#8a8374' }}>
          Loading contacts...
        </div>
      ) : contacts.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#8a8374"
              strokeWidth="1.6"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18M9 21V9" />
            </svg>
          </div>
          <p className="empty-title">No contacts yet</p>
          <p className="empty-copy">
            Click "Refresh" above to sync from your Google Sheet.
          </p>
        </div>
      ) : (
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          <table style={{ fontSize: '13px' }}>
            <tbody>
              {contacts.map((contact) => (
                <tr key={contact.id} style={{ borderBottom: '1px solid #EAE3CF' }}>
                  <td style={{ padding: '10px', color: '#1C1B18' }}>
                    {contact.name}
                  </td>
                  <td style={{ padding: '10px', color: '#8a8374', textAlign: 'right' }}>
                    {contact.phone}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ fontSize: '12px', color: '#8a8374', padding: '12px', margin: 0, borderTop: '1px solid #EAE3CF' }}>
            <b>{contacts.length}</b> total contacts
          </p>
        </div>
      )}

      <p className="footnote">
        Synced from Google Sheets. Reads <b>Vārds</b> (Name) and <b>Telefona nr</b> (Phone) columns.
      </p>
    </div>
  )
}
