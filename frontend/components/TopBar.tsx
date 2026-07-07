interface TopBarProps {
  metaConnected: boolean
  sheetConnected: boolean
}

export default function TopBar({ metaConnected, sheetConnected }: TopBarProps) {
  return (
    <div className="topbar">
      <div className="brand">
        <span className="brand-mark">Lāceni</span>
        <span className="brand-sub">WhatsApp Sūtne</span>
      </div>
      <div className="conn-status">
        <div className="conn-pill">
          <span className={`dot ${metaConnected ? 'live' : ''}`}></span>
          Meta Business — {metaConnected ? 'connected' : 'not connected'}
        </div>
        <div className="conn-pill">
          <span className={`dot ${sheetConnected ? 'live' : ''}`}></span>
          Google Sheet — {sheetConnected ? 'connected' : 'not connected'}
        </div>
      </div>
    </div>
  )
}
