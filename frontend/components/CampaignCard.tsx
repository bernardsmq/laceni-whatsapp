'use client'

import { useState, useEffect } from 'react'

interface CampaignCardProps {
  templateConnected: boolean
  contactsConnected: boolean
}

interface Template {
  id: string
  name: string
  body: string
}

interface Contact {
  id: string
  name: string
  phone: string
}

export default function CampaignCard({
  templateConnected,
  contactsConnected,
}: CampaignCardProps) {
  const [templates, setTemplates] = useState<Template[]>([])
  const [contacts, setContacts] = useState<Contact[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [namePreview, setNamePreview] = useState('')
  const [testPhoneNumber, setTestPhoneNumber] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (templateConnected) {
      fetchTemplates()
    }
  }, [templateConnected])

  useEffect(() => {
    if (contactsConnected) {
      fetchContacts()
    }
  }, [contactsConnected])

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/templates')
      const data = await response.json()
      console.log('Templates response:', data)
      if (response.ok) {
        setTemplates(data.templates || [])
      } else {
        console.error('Template fetch error:', data)
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
  }

  const fetchContacts = async () => {
    try {
      const response = await fetch('/api/contacts')
      if (response.ok) {
        const data = await response.json()
        setContacts(data.contacts || [])
      }
    } catch (error) {
      console.error('Failed to fetch contacts:', error)
    }
  }

  const handleSendCampaign = async () => {
    if (!selectedTemplate || !contactsConnected) {
      setError('Please select a template and ensure contacts are connected')
      return
    }

    setSending(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch('/api/campaigns/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: selectedTemplate,
        }),
      })

      if (response.ok) {
        setSuccess(`Campaign sent to ${contacts.length} recipients`)
        setSelectedTemplate('')
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to send campaign')
      }
    } catch (error) {
      setError('Failed to send campaign')
      console.error(error)
    } finally {
      setSending(false)
    }
  }

  const getSelectedTemplateBody = () => {
    const template = templates.find((t) => t.id === selectedTemplate)
    return template?.body || 'Select a template to see preview'
  }

  const previewMessage = getSelectedTemplateBody().replace(
    '{{1}}',
    namePreview ? `<span class="ph">${namePreview}</span>` : '<span class="ph">{{1}}</span>'
  )

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <p className="card-eyebrow">Send campaign</p>
          <h3 className="card-title">Compose &amp; send</h3>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="row">
        <div>
          <label className="field-label">Template</label>
          <select
            value={selectedTemplate}
            onChange={(e) => setSelectedTemplate(e.target.value)}
            disabled={!templateConnected}
          >
            <option value="">
              {templateConnected
                ? 'Select a template'
                : 'No templates available — connect Meta account'}
            </option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="field-label">Recipients</label>
          <input
            type="text"
            disabled
            value={
              contactsConnected ? `${contacts.length} contacts synced` : 'No contacts'
            }
            readOnly
          />
        </div>
      </div>

      <label className="field-label">Preview personalization</label>
      <input
        type="text"
        placeholder="Type a name to preview the merge field, e.g. Anna"
        value={namePreview}
        onChange={(e) => setNamePreview(e.target.value)}
        style={{ marginBottom: '12px' }}
      />
      <div
        className="preview-box"
        dangerouslySetInnerHTML={{ __html: previewMessage }}
      />

      <div className="send-footer">
        <div className="recipient-count">
          Recipients: <b>{contacts.length}</b> / {contacts.length} synced
        </div>
        <button
          className="btn btn-primary"
          disabled={!selectedTemplate || !contactsConnected || sending}
          onClick={handleSendCampaign}
          title={
            !selectedTemplate || !contactsConnected
              ? 'Connect a template and contact list first'
              : ''
          }
        >
          {sending ? 'Sending...' : 'Send campaign'}
        </button>
      </div>
      <p className="footnote">
        Sending stays disabled until a template and a synced contact list are
        both selected — this prevents sending to an empty or stale list by
        accident.
      </p>

      <hr style={{ margin: '24px 0', border: 'none', borderTop: '1px solid #EAE3CF' }} />

      <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#f9f5ed', borderRadius: '8px' }}>
        <h4 style={{ margin: '0 0 12px 0', fontSize: '13px', fontWeight: 'bold' }}>🧪 Test Send (Debug)</h4>
        <p style={{ margin: '0 0 12px 0', fontSize: '12px', color: '#8a8374' }}>
          Manually test sending a message to a specific phone number
        </p>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
          <input
            type="text"
            placeholder="Phone number (e.g. 37126713717)"
            style={{
              flex: 1,
              padding: '8px 12px',
              border: '1px solid #EAE3CF',
              borderRadius: '6px',
              fontSize: '12px',
            }}
            value={testPhoneNumber}
            onChange={(e) => setTestPhoneNumber(e.target.value)}
          />
          <button
            className="btn btn-primary"
            style={{ fontSize: '12px', padding: '8px 16px' }}
            onClick={async () => {
              const phoneNum = testPhoneNumber
              if (!phoneNum) {
                setError('Please enter a phone number')
                return
              }
              setSending(true)
              try {
                // Personalize message with name from preview field
                const personalizedMessage = getSelectedTemplateBody().replace(
                  '{{1}}',
                  namePreview || 'Friend'
                )
                const response = await fetch('/api/campaigns/send-test', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    phone_number: phoneNum,
                    message: personalizedMessage,
                  }),
                })
                const result = await response.json()
                if (response.ok) {
                  setSuccess(`✅ Test message sent to +${phoneNum}`)
                } else {
                  setError(`❌ ${result.detail || 'Failed to send test message'}`)
                }
              } catch (err) {
                setError('Error sending test message')
              } finally {
                setSending(false)
              }
            }}
            disabled={sending || !testPhoneNumber}
          >
            {sending ? 'Sending...' : 'Send Test'}
          </button>
        </div>
        <div style={{ fontSize: '11px', color: '#8a8374', marginTop: '8px' }}>
          <p style={{ margin: '4px 0' }}>📝 Total templates loaded: <strong>{templates.length}</strong></p>
          <p style={{ margin: '4px 0' }}>📞 Total contacts: <strong>{contacts.length}</strong></p>
        </div>
      </div>
    </div>
  )
}
