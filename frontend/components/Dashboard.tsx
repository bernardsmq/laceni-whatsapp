import { useState, useEffect } from 'react'
import TopBar from './TopBar'
import TemplatesCard from './TemplatesCard'
import ContactsCard from './ContactsCard'
import CampaignCard from './CampaignCard'
import TrackingCard from './TrackingCard'
import SettingsModal from './SettingsModal'

export default function Dashboard() {
  const [metaConnected, setMetaConnected] = useState(false)
  const [sheetConnected, setSheetConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [settingsOpen, setSettingsOpen] = useState(false)

  useEffect(() => {
    checkConnectionStatus()
  }, [])

  const checkConnectionStatus = async () => {
    try {
      const response = await fetch('/api/status')
      if (response.ok) {
        const data = await response.json()
        setMetaConnected(data.meta_connected)
        setSheetConnected(data.sheet_connected)
      }
    } catch (error) {
      console.error('Failed to check connection status:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <TopBar
        metaConnected={metaConnected}
        sheetConnected={sheetConnected}
        onSettingsClick={() => setSettingsOpen(true)}
      />
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => {
          setSettingsOpen(false)
          checkConnectionStatus()
        }}
      />
      <div className="shell">
        <div>
          <TemplatesCard connected={metaConnected} />
          <ContactsCard connected={sheetConnected} />
        </div>
        <div>
          <CampaignCard
            templateConnected={metaConnected}
            contactsConnected={sheetConnected}
          />
          <TrackingCard />
        </div>
      </div>
    </div>
  )
}
