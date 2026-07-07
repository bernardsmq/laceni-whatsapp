import { useState, useEffect } from 'react'
import TopBar from './TopBar'
import TemplatesCard from './TemplatesCard'
import ContactsCard from './ContactsCard'
import CampaignCard from './CampaignCard'
import TrackingCard from './TrackingCard'

export default function Dashboard() {
  const [metaConnected, setMetaConnected] = useState(false)
  const [sheetConnected, setSheetConnected] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkConnectionStatus()
  }, [])

  const checkConnectionStatus = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/status`,
        {
          headers: {
            Authorization: `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
          },
        }
      )
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
      />
      <div className="shell">
        <div>
          <TemplatesCard
            connected={metaConnected}
            onConnect={() => window.location.href = '/api/auth/meta-whatsapp'}
          />
          <ContactsCard
            connected={sheetConnected}
            onConnect={() => window.location.href = '/api/auth/google-sheets'}
          />
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
