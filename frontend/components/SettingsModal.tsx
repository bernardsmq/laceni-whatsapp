'use client'

import { useState } from 'react'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [metaPhoneId, setMetaPhoneId] = useState('')
  const [metaAccessToken, setMetaAccessToken] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleSave = async () => {
    setSaving(true)
    setMessage('')

    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          meta_phone_id: metaPhoneId,
          meta_access_token: metaAccessToken,
        }),
      })

      if (response.ok) {
        setMessage('✅ Settings saved!')
        setTimeout(() => {
          onClose()
        }, 1500)
      } else {
        setMessage('❌ Failed to save settings')
      }
    } catch (error) {
      setMessage('❌ Error saving settings')
      console.error(error)
    } finally {
      setSaving(false)
    }
  }

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div className="card" style={{ maxWidth: '500px', width: '90%' }}>
        <div className="card-head">
          <h3 className="card-title">Meta WhatsApp Settings</h3>
        </div>

        {message && (
          <div
            style={{
              padding: '12px',
              marginBottom: '12px',
              borderRadius: '8px',
              backgroundColor: message.includes('✅') ? '#e8ffe8' : '#ffe8e8',
              color: message.includes('✅') ? '#2e7d32' : '#c4482f',
              fontSize: '13px',
            }}
          >
            {message}
          </div>
        )}

        <div style={{ marginBottom: '16px' }}>
          <label className="field-label">Phone Number ID</label>
          <input
            type="text"
            placeholder="Your WhatsApp Business Phone Number ID"
            value={metaPhoneId}
            onChange={(e) => setMetaPhoneId(e.target.value)}
            disabled={saving}
          />
          <p style={{ fontSize: '11px', color: '#8a8374', marginTop: '4px' }}>
            Find this in Meta Business Manager → WhatsApp → Phone numbers
          </p>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label className="field-label">Access Token</label>
          <textarea
            placeholder="Your Meta access token"
            value={metaAccessToken}
            onChange={(e) => setMetaAccessToken(e.target.value)}
            disabled={saving}
            style={{
              width: '100%',
              padding: '10px 12px',
              border: '1px solid #EAE3CF',
              borderRadius: '8px',
              fontSize: '12px',
              minHeight: '100px',
              fontFamily: 'monospace',
            } as React.CSSProperties}
          />
          <p style={{ fontSize: '11px', color: '#8a8374', marginTop: '4px' }}>
            Get this from Meta Business Manager → Settings → Apps and websites
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            className="btn btn-ghost"
            onClick={onClose}
            disabled={saving}
          >
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={saving || !metaPhoneId || !metaAccessToken}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}
