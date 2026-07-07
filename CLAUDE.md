# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Lāceni WhatsApp Dashboard** — A WhatsApp business messaging platform that lets Lāceni restaurant (Latvian brand) send personalized bulk campaigns to opted-in contacts.

**Core flow:** Connect Google Sheets (contact list) → Connect Meta WhatsApp (approved templates) → Select template + send → Track delivery/reads

## Architecture

### Frontend (Next.js 14 TypeScript)
- `app/layout.tsx` — Root layout, metadata
- `app/page.tsx` — Entry point
- `app/globals.css` — Shared styles (dark topbar, yellow accents, cream background)
- `components/Dashboard.tsx` — Main orchestrator, loads all sub-components
- `components/{TopBar,TemplatesCard,ContactsCard,CampaignCard,TrackingCard}.tsx` — UI components

**Key design:** Components are mostly presentational. The `CampaignCard` is the most stateful (handles form, API calls, preview generation).

### Backend (FastAPI Python)
- `app/main.py` — FastAPI app, CORS, route registration
- `app/config.py` — Environment variables (Pydantic Settings)
- `app/api/{auth,templates,contacts,campaigns,logs}.py` — Route handlers
- `app/services/{supabase_client,google_sheets_service,meta_service}.py` — Integration logic

**Key pattern:** Each `app/api/*.py` file is a router module with endpoints. Services handle external APIs (Google Sheets, Meta, Supabase).

### Database (Supabase PostgreSQL)
- `supabase/migrations/001_initial_schema.sql` — Creates tables: `oauth_credentials`, `contacts`, `message_templates`, `send_logs`
- RLS (Row Level Security) enabled, service role can access all
- Indexes on `provider`, `phone`, `sent_at` for performance

## Development Commands

```bash
# Frontend
npm run dev              # Next.js dev server (port 3000)
npm run build           # Production build
npm run type-check      # TypeScript type checking
npm run lint            # ESLint

# Backend
python -m uvicorn app.main:app --reload  # FastAPI dev (port 8000, auto-reload)

# Local (with Docker Compose)
docker-compose up       # Spins up backend, frontend, postgres

# Deployment
# Push to GitHub → Railway auto-detects Dockerfile and deploys
```

## Key Implementation Details

### OAuth Flows
- **Google Sheets:** User clicks "Connect Google Sheet" → redirects to Google OAuth → callback stores `access_token` + `refresh_token` in `oauth_credentials` table
- **Meta WhatsApp:** Similar flow, stores credentials for later API calls
- Credentials auto-refresh on expiry (in `GoogleSheetsService`)

### Contact Sync
- Google Sheets has 2 columns: Name (A), Phone (B)
- `GET /api/contacts` reads from `contacts` table (cached from last sync)
- `POST /api/sync-contacts` fetches fresh data from Sheets, clears and re-inserts into `contacts` table
- **Currently manual sync**, but can be automated with a background job (e.g., APScheduler)

### Campaign Send
- User selects template + previews personalization ({{name}} → contact name)
- `POST /api/campaigns/send` iterates all contacts, calls Meta API for each
- Each message personalizes the template body
- Logs entry created with sent/failed counts
- **Frontend polling:** Tracking card polls `/api/logs` every 10 seconds for delivery status

### Message Personalization
- Template from Meta: `"Sveiki, {{name}} 👋 ..."`
- Backend: replaces `{{name}}` with contact's name before sending
- Frontend preview: real-time preview as user types name in input

## File Locations & Common Tasks

| Task | File |
|------|------|
| Add new API endpoint | `backend/app/api/[module].py`, register in `main.py` |
| Add component | `frontend/components/NewComponent.tsx`, import in Dashboard |
| Add Supabase table | `supabase/migrations/[next_number].sql`, run via Supabase CLI |
| Change styling | `frontend/app/globals.css` (uses CSS vars: `--yellow`, `--cream`, `--ink`, etc.) |
| Add env variable | `.env.example`, then `app/config.py` (backend) or inline (frontend) |

## Important Patterns & Conventions

1. **Environment variables**
   - Frontend: `NEXT_PUBLIC_*` prefix for browser-accessible vars (Supabase anon key)
   - Backend: Use `app/config.py` Settings class (Pydantic validates types)
   - Never commit `.env`, always update `.env.example`

2. **API error handling**
   - Backend raises `HTTPException(status_code=..., detail=...)` 
   - Frontend catches, displays in error box (`.error-message` CSS class)

3. **Async patterns**
   - Frontend: `useEffect` + `fetch()` (no async/await in effects, use callback)
   - Backend: FastAPI endpoints are async, services are async

4. **Supabase**
   - Always use service role key on backend (not anon key)
   - RLS policies are set up but permissive (service role bypasses)
   - Credentials stored as JSON in `metadata` column for flexibility

5. **Styling**
   - No Tailwind, pure CSS with semantic color variables
   - Responsive breakpoints: `@media (max-width: 880px)` for grid, `560px` for row
   - Yellow accent (`--yellow: #F6C90E`) used for interactive states, emphasis

## Deployment to Railway

1. Push to GitHub: `git push -u origin main`
2. Railway auto-detects Dockerfile
3. Add env vars in Railway dashboard
4. Railway builds and deploys automatically
5. Update OAuth redirect URIs in Google Cloud + Meta to match Railway domain

**Port forwarding:** Frontend runs on 3000, backend on 8000 (see `docker-entrypoint.sh` and Dockerfile)

## Testing & Validation

- **Frontend:** No test files currently. Manual testing via browser (http://localhost:3000)
- **Backend:** No test files currently. Use Postman/curl or FastAPI `/docs` Swagger UI
- **Database:** Query directly via Supabase UI or `psql` CLI

**Quick validate:**
```bash
# Backend health
curl http://localhost:8000/health

# Frontend loads
curl http://localhost:3000
```

## Known Limitations & TODOs

1. **Auto-sync not implemented** — Contact sync is manual (`POST /api/sync-contacts`). Add APScheduler job for hourly sync.
2. **No authentication** — Dashboard is public. Add user auth if needed.
3. **Message status tracking incomplete** — Logs created but delivery/read webhooks from Meta not wired up.
4. **No error retry** — Failed sends are logged but not retried. Consider exponential backoff.
5. **Google credentials file** — Currently expects `credentials.json` in root. Make configurable.
6. **Meta API mocking** — In development, messages don't actually send (would need test account).

## Quick Fixes & Common Issues

| Issue | Fix |
|-------|-----|
| "CORS error" | Check `allow_origins` in `main.py` (currently `["*"]`) |
| "Google Sheets not found" | Verify sheet ID is stored in `oauth_credentials.metadata` |
| "Templates loading slow" | Cache template list in frontend state, add loading skeleton |
| "Duplicate contacts after sync" | Schema has no unique constraint on phone; add if needed |
| "401 Unauthorized to Supabase" | Check `SUPABASE_SERVICE_ROLE_KEY` vs `SUPABASE_KEY` (service role is for backend) |

## Code Style

- **Frontend:** TypeScript strict mode, component naming PascalCase, hooks only in client components (`'use client'`)
- **Backend:** Python type hints (Pydantic models for request/response), snake_case for DB columns
- **No comments:** Only add comments for non-obvious logic (e.g., credential refresh strategy)

## Next Priority Tasks

Based on the codebase, next steps are usually:
1. Wire up OAuth flows (currently stubbed, need actual Google Cloud + Meta setup)
2. Implement message status webhook from Meta (delivery/read tracking)
3. Add contact auto-sync background job
4. Add user authentication & multi-tenant support if needed
5. Build test suite (pytest backend, Jest frontend)
