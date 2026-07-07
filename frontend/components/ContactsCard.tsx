interface ContactsCardProps {
  connected: boolean
  onConnect: () => void
}

export default function ContactsCard({ connected, onConnect }: ContactsCardProps) {
  return (
    <div className="card">
      <div className="card-head">
        <div>
          <p className="card-eyebrow">Google Sheets</p>
          <h3 className="card-title">Contact list</h3>
        </div>
      </div>
      {!connected ? (
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
          <p className="empty-title">No sheet connected</p>
          <p className="empty-copy">
            Connect the sheet with Name and Phone columns to pull your opted-in
            subscribers.
          </p>
          <button className="btn btn-primary" onClick={onConnect}>
            Connect Google Sheet
          </button>
        </div>
      ) : (
        <div className="empty">
          <p className="empty-title">Sheet connected</p>
          <p className="empty-copy">
            Contacts will sync automatically from your Google Sheet.
          </p>
        </div>
      )}
      <p className="footnote">
        Reads two columns only: <b>Name</b> and <b>Phone</b>. Only rows added
        through your consented opt-in flow should be in this sheet.
      </p>
    </div>
  )
}
