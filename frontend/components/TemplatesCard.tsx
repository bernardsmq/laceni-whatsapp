interface TemplatesCardProps {
  connected: boolean
}

export default function TemplatesCard({ connected }: TemplatesCardProps) {
  return (
    <div className="card">
      <div className="card-head">
        <div>
          <p className="card-eyebrow">Meta Business</p>
          <h3 className="card-title">Message templates</h3>
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
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
            </svg>
          </div>
          <p className="empty-title">Meta not configured</p>
          <p className="empty-copy">
            Click Settings (⚙️) to add your Meta WhatsApp credentials.
          </p>
        </div>
      ) : (
        <div className="empty">
          <p className="empty-title">✅ Meta connected</p>
          <p className="empty-copy">
            Templates are ready. Select one in the campaign section to send.
          </p>
        </div>
      )}
    </div>
  )
}
