# Lāceni WhatsApp Dashboard

WhatsApp message campaign manager for Lāceni restaurant. Send personalized bulk messages to opted-in contacts using WhatsApp Business API.

## Features

- **Google Sheets Integration** — Connect once, automatically syncs contact list (Name + Phone)
- **Meta WhatsApp Business** — Select approved message templates and send campaigns
- **Personalized Messages** — Auto-replace `{{name}}` placeholder with each recipient's name
- **Message Tracking** — View sent, delivered, and read stats with campaign history
- **Export Logs** — CSV export of all sent campaigns

## Architecture

- **Frontend**: Next.js 14 (TypeScript)
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Railway (Docker)

## Local Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (optional)
- Supabase project (sign up at supabase.com)
- Google Cloud project with Sheets API enabled
- Meta WhatsApp Business account

### 1. Clone & Install

```bash
git clone https://github.com/bernardsmq/laceni-whatsapp.git
cd laceni-whatsapp

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Environment Setup

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Required credentials:**

#### Supabase
- `NEXT_PUBLIC_SUPABASE_URL` — Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` — Supabase service role key (for backend)

#### Google Sheets API
- `GOOGLE_CLIENT_ID` — From Google Cloud Console
- `GOOGLE_CLIENT_SECRET` — From Google Cloud Console
- `GOOGLE_REDIRECT_URI` — `http://localhost:3000/api/auth/google-sheets/callback`

#### Meta WhatsApp
- Setup guide: https://developers.facebook.com/docs/whatsapp/business-platform
- You'll fill these in after connecting through the dashboard

### 3. Database Setup

1. Create new Supabase project
2. Run migrations: Connect to your Supabase PostgreSQL and execute `supabase/migrations/001_initial_schema.sql`
3. Update `.env` with Supabase credentials

### 4. Run Locally

**Option A: Separate terminals**

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open http://localhost:3000

**Option B: Docker Compose**

```bash
docker-compose up
```

## Deployment to Railway

### 1. Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/bernardsmq/laceni-whatsapp.git
git push -u origin main
```

### 2. Deploy to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `laceni-whatsapp` repository
4. Railway will auto-detect the Dockerfile
5. Add environment variables in Railway dashboard (copy from `.env`)
6. Deploy!

### 3. Configure Domain

In Railway dashboard:
1. Go to Settings → Domains
2. Add custom domain or use Railway's default
3. Update `GOOGLE_REDIRECT_URI` in Google Cloud Console to your Railway URL

## API Endpoints

### Authentication

- `GET /api/auth/google-sheets` — Initiate Google Sheets OAuth
- `GET /api/auth/google-sheets/callback` — OAuth callback
- `GET /api/auth/meta-whatsapp` — Initiate Meta OAuth
- `GET /api/auth/meta-whatsapp/callback` — OAuth callback

### Templates

- `GET /api/templates` — List approved WhatsApp message templates

### Contacts

- `GET /api/contacts` — List synced contacts
- `POST /api/sync-contacts` — Manually trigger Google Sheets sync

### Campaigns

- `POST /api/campaigns/send` — Send campaign to all contacts

### Logs

- `GET /api/logs` — Get send logs and stats
- `GET /api/logs/export` — Export logs as CSV

### Health

- `GET /health` — Health check
- `GET /api/status` — Check connection status (Meta & Google Sheets)

## Google Sheets Format

Your Google Sheet must have exactly 2 columns (no headers required, but recommended):

| Name  | Phone |
|-------|-------|
| Anna  | +1234567890 |
| Bob   | +1987654321 |

- Column A: Contact name (used for {{name}} personalization)
- Column B: Phone number (international format with + prefix)

## Message Template Format

WhatsApp templates use this format for personalization:

```
Sveiki, {{1}} 👋 Šodienas pusdienu piedāvājums Lāceni gaida jūs no plkst. 12:00!
```

The `{{1}}` or `{{name}}` placeholder will be replaced with each contact's name.

## Troubleshooting

### "Google Sheets not connected"
- Check Google Cloud Console: Sheets API must be enabled
- OAuth consent screen must be configured
- Credentials must be downloaded as JSON

### "No contacts synced"
- Ensure Google Sheet has Name and Phone columns
- Click "Sync contacts" button or the system syncs automatically
- Check that phone numbers are in international format

### "Templates not loading"
- Meta account must have approved message templates
- Account must have correct permissions for WhatsApp Business API
- Check Meta API rate limits

## Development

### Commands

```bash
# Frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run lint         # Lint code
npm run type-check   # TypeScript check

# Backend
python -m uvicorn app.main:app --reload  # Dev server
python -m pytest                           # Run tests (if added)
```

### Database

Access Supabase PostgreSQL directly:

```bash
psql postgresql://user:password@db.supabase.co:5432/postgres
```

## License

MIT

## Support

For issues or questions, create a GitHub issue or contact support.
