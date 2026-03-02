# Concertiv AI Proposal Generator — POC

A proof-of-concept system that automates the extraction of final agreed commercial terms from multi-round vendor negotiation email threads, with human review and branded PDF proposal generation powered by Claude AI.

---

## Overview

Concertiv is a procurement intermediary that negotiates commercial terms between financial services clients and vendors over email. Manually extracting final agreed terms from 7–15 email threads takes 30–60 minutes per deal and is prone to errors.

This POC demonstrates:
- Automated extraction of structured commercial terms from unstructured email negotiations using Claude AI
- Confidence scoring (HIGH / MEDIUM / LOW) with ambiguity flagging
- Price history tracking across multi-round negotiations
- A human-in-the-loop review UI before final proposal generation
- Branded PDF proposal output

**POC Results:** 3 test scenarios with correct extraction accuracy, all 54 automated tests passing, end-to-end processing in under 10 seconds per thread.

---

## Architecture

```
Upload JSON → Parse Thread → Ingest to DB → Flatten Thread →
Claude AI Extraction → Validation → Review in UI → Generate PDF → Download
```

The system has three components:

| Component | Stack | Port |
|-----------|-------|------|
| Backend API | Django + Django REST Framework | 8000 |
| Frontend UI | React 19 + Zustand | 3000 |
| Dummy Outlook | Flask (mock server for testing) | 5000 |

---

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- An [Anthropic API key](https://console.anthropic.com/)

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework django-cors-headers \
            anthropic weasyprint python-dotenv jinja2

# Configure environment
cp .env.example .env            # then fill in your values
```

**.env file:**
```env
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_MAX_TOKENS=4096
USE_MOCK_EXTRACTION=false       # Set to 'true' to skip API calls during testing
```

```bash
# Run database migrations
python manage.py migrate

# Load sample test threads
python manage.py load_dummy_threads

# Start the server
python manage.py runserver      # http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start                       # http://localhost:3000
```

### Dummy Outlook Mock Server (optional)

```bash
cd dummy-outlook
pip install flask flask-cors
python app.py                   # http://localhost:5000
```

---

## Usage

The UI walks through three screens:

1. **Upload** — Drag-and-drop or paste a JSON email thread
2. **Review** — Side-by-side view of the original thread and AI-extracted fields; edit any field before generating
3. **Preview** — View the rendered HTML proposal and download as PDF

### Sample Data

Three realistic test scenarios are included in `backend/data/threads/`:

| File | Scenario |
|------|----------|
| `thread_001_happy_path.json` | Bloomberg Terminal renewal with explicit acceptance |
| `thread_002_multi_round.json` | Complex multi-round negotiation |
| `thread_003_ambiguous_close.json` | Negotiation with unresolved ambiguities |

---

## What Claude Extracts

| Category | Fields |
|----------|--------|
| **Parties** | Client, vendor, Concertiv contacts |
| **Product** | Name, description, inclusions/exclusions |
| **Pricing** | Unit price, quantity, annual value, contract value, currency, escalation cap, full price history |
| **License Terms** | Duration, start/end dates, seat count, usage type, renewal type |
| **SLA** | Uptime commitment, support tier |
| **Meta** | Confidence level, acceptance signal quote, ambiguities |

**Confidence scoring:**
- **HIGH** — Explicit acceptance signal + all key fields present + no ambiguities
- **MEDIUM** — Implied acceptance or minor missing fields
- **LOW** — No clear acceptance or significant unresolved terms

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/threads/upload/` | Upload email thread (JSON or file) |
| `GET` | `/api/threads/` | List all threads |
| `GET` | `/api/threads/{id}/` | Get thread detail with messages |
| `POST` | `/api/threads/{id}/analyze/` | Trigger Claude AI extraction |
| `GET` | `/api/proposals/{id}/` | Get extracted proposal |
| `PATCH` | `/api/proposals/{id}/` | Edit extracted fields |
| `POST` | `/api/proposals/{id}/generate/` | Generate HTML/PDF proposal |
| `GET` | `/api/proposals/{id}/download/` | Download PDF |
| `POST` | `/api/outlook/fetch/` | Fetch thread from Outlook (stub) |

---

## Testing

```bash
# Backend (54 tests)
cd backend
python manage.py test

# Frontend
cd frontend
npm test

# Production build check
npm run build
```

---

## Project Structure

```
ConcertivPOC/
├── backend/
│   ├── config/                  # Django settings & URL routing
│   ├── threads/                 # Email thread ingestion & models
│   ├── extraction/              # Claude AI client, prompts, validator
│   ├── proposals/               # PDF generation (Jinja2 + WeasyPrint)
│   ├── outlook/                 # Microsoft Graph integration stubs
│   ├── tests/                   # Test suite
│   └── data/threads/            # Sample JSON test data
├── frontend/
│   └── src/
│       ├── components/          # ThreadInput, ProposalReview, ProposalPreview
│       ├── services/api.js      # Axios API client
│       ├── store/useStore.js    # Zustand state management
│       └── App.js               # Main app with screen routing
├── dummy-outlook/               # Flask mock Outlook server for testing
└── ARCHITECTURE_AND_ROADMAP.md  # Detailed architecture & production roadmap
```

---

## Production Roadmap

| Phase | Timeline | Highlights |
|-------|----------|------------|
| Internal Pilot | Weeks 1–3 | Azure App Service, PostgreSQL, Azure AD auth, live Outlook pull |
| Team Rollout | Weeks 4–6 | Async processing (Celery + Redis), webhooks, audit logging |
| Full Production | Weeks 7–10 | Shared mailbox monitoring, CRM integration, deal pipeline dashboard |

See [`ARCHITECTURE_AND_ROADMAP.md`](./ARCHITECTURE_AND_ROADMAP.md) for the full technical specification.

---

## Security Notes

This POC runs on localhost with no authentication and uses SQLite. Before any production deployment:

- Enable Azure AD SSO (staff-only access)
- Migrate to PostgreSQL with encryption at rest
- Store secrets in Azure Key Vault
- Enforce HTTPS and VPN access
- Implement audit trail logging and data retention policies

---

## License

Internal proof-of-concept. Not for external distribution.
