# Concertiv Intelligent Proposal Generation
# Architecture Document & Production Roadmap

**Prepared by:** Engineering Team
**Date:** February 24, 2026
**Status:** POC Complete | Production Integration Planned
**Confidential**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture (Current POC)](#2-system-architecture-current-poc)
3. [End-to-End Workflow](#3-end-to-end-workflow)
4. [Database Schema](#4-database-schema)
5. [API Specification](#5-api-specification)
6. [AI Extraction Engine](#6-ai-extraction-engine)
7. [Production Integration: Outlook + Microsoft Graph](#7-production-integration-outlook--microsoft-graph)
8. [Production Architecture (Target State)](#8-production-architecture-target-state)
9. [Security & Compliance Considerations](#9-security--compliance-considerations)
10. [Migration Plan: POC to Production](#10-migration-plan-poc-to-production)

---

## 1. Executive Summary

### What This System Does

Concertiv acts as a procurement intermediary between financial services clients and vendors. Our team facilitates multi-round negotiations via email between clients, vendors, and Concertiv account managers. These negotiations result in agreed commercial terms (pricing, licenses, SLAs) that need to be captured in formal proposal documents.

**The Problem:** Manually reading through 7-15 email threads, extracting final agreed terms from multi-round negotiations, and assembling proposal documents is time-consuming (30-60 minutes per deal) and error-prone.

**The Solution:** An AI-powered system that:
- Ingests email conversation threads
- Uses Claude AI to automatically extract final agreed commercial terms
- Detects acceptance signals and flags unresolved ambiguities
- Generates professional, branded PDF proposals
- Allows human review and editing before finalization

### POC Results

| Metric | Result |
|--------|--------|
| Threads tested | 3 (happy path, complex multi-round, ambiguous) |
| Extraction accuracy | Correct pricing, parties, and terms on all 3 scenarios |
| Confidence detection | Correctly assigned HIGH, MEDIUM, LOW respectively |
| Ambiguity detection | Flagged 4 ambiguities on the ambiguous thread |
| Price history tracking | Captured all negotiation rounds (3, 5, and 3 rounds) |
| End-to-end time | < 10 seconds per thread (upload to PDF) |
| Test coverage | 54 automated tests, all passing |

---

## 2. System Architecture (Current POC)

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, Zustand, Axios | 3-screen UI for upload, review, download |
| Backend API | Django 4.2, Django REST Framework | REST API, business logic, data persistence |
| AI Engine | Claude API (Anthropic SDK) | Commercial term extraction from email text |
| PDF Generation | WeasyPrint, Jinja2 | HTML-to-PDF conversion with branding |
| Database | SQLite (POC) / PostgreSQL (Production) | Structured data storage with JSON fields |

### Component Diagram

```
                        ┌──────────────────────┐
                        │      End User        │
                        │  (Concertiv Staff)   │
                        └──────────┬───────────┘
                                   │
                         Browser (localhost:3000)
                                   │
                        ┌──────────▼───────────┐
                        │     React Frontend   │
                        │                      │
                        │  Screen 1: Upload    │
                        │  Screen 2: Review    │
                        │  Screen 3: Preview   │
                        └──────────┬───────────┘
                                   │
                            REST API (JSON)
                            Port 8000
                                   │
                        ┌──────────▼───────────┐
                        │   Django Backend     │
                        │                      │
                        │  ┌─────────────────┐ │
                        │  │ Thread Service  │ │──── Ingestion & Flattening
                        │  └────────┬────────┘ │
                        │           │          │
                        │  ┌────────▼────────┐ │
                        │  │ Claude Client   │ │──── AI Extraction
                        │  │ (Anthropic SDK) │ │
                        │  └────────┬────────┘ │
                        │           │          │
                        │  ┌────────▼────────┐ │
                        │  │ Proposal Gen    │ │──── HTML/PDF Generation
                        │  │ (Jinja2+Weasy)  │ │
                        │  └─────────────────┘ │
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
             ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
             │   SQLite    │ │ Claude   │ │ File       │
             │   Database  │ │ API      │ │ Storage    │
             │ (4 tables)  │ │(Anthropic)│ │ (PDFs)    │
             └─────────────┘ └──────────┘ └────────────┘
```

---

## 3. End-to-End Workflow

### Step-by-Step Flow

```
STEP 1: UPLOAD                    STEP 2: INGEST
─────────────                     ──────────────
User uploads ──→ POST /api/     ──→ ThreadIngestionService
JSON file       threads/upload/     ├── Parse JSON structure
                                    ├── Create EmailThread record
                                    ├── Create EmailMessage records (per email)
                                    ├── Build flattened chronological text
                                    └── Store all in database


STEP 3: EXTRACT                   STEP 4: REVIEW
───────────────                   ──────────────
POST /api/threads/  ──→ Claude   ──→ React displays side-by-side:
{id}/analyze/          API call      Left:  Original email thread
                       │             Right: Extracted fields (editable)
                       ▼             Top:   Confidence badge + warnings
                  Parse + Validate
                  + Adjust Confidence
                       │
                       ▼
                  Save to ExtractedProposal table


STEP 5: EDIT (optional)           STEP 6: GENERATE
───────────────────────           ─────────────────
User edits field ──→ PATCH       POST /api/proposals/ ──→ ProposalGenerator
                     /api/       {id}/generate/           ├── Render Jinja2 template
                     proposals/                           ├── Build executive summary
                     {id}/                                ├── Apply Concertiv branding
                                                          ├── WeasyPrint → PDF bytes
                                                          └── Save HTML + PDF to DB


STEP 7: DOWNLOAD
────────────────
GET /api/proposals/{id}/download/ ──→ Stream PDF to browser
```

### What the AI Extracts

Claude analyzes the full email thread and produces a structured JSON with:

| Field | Description | Example |
|-------|-------------|---------|
| **parties** | Client, Vendor, Concertiv contacts | Acme Capital, Bloomberg LP |
| **product** | Product name, description, inclusions/exclusions | Bloomberg Terminal |
| **pricing** | Unit price, quantity, annual/contract value | $20,500/seat x 18 = $369K/yr |
| **price_history** | Every negotiation round with proposer and amount | Round 1: $21,500 → Round 3: $20,500 |
| **license_terms** | Duration, dates, seat count, renewal type | 2 years, Mar 2025 - Feb 2027 |
| **sla_terms** | Uptime commitment, support tier | 99.9% uptime, Premium support |
| **special_conditions** | Escalation caps, pilots, MFN clauses | 3% Year 2 price cap |
| **ambiguities** | Unresolved items flagged for human review | "Renewal type not specified" |
| **confidence** | HIGH / MEDIUM / LOW reliability score | Based on acceptance signals |
| **acceptance_signal** | The exact quote showing agreement | "That works for us. Please proceed." |

### Confidence Scoring Rules

| Level | Criteria |
|-------|----------|
| **HIGH** | Explicit acceptance found ("agreed", "confirmed", "please proceed"), no ambiguities, all key fields present |
| **MEDIUM** | Implied acceptance (next steps discussed), or has minor ambiguities, or some fields missing |
| **LOW** | No acceptance signal found, unresolved counter-offers, significant ambiguities, or key data missing |

---

## 4. Database Schema

### Entity Relationship

```
EmailThread (1) ──── (N) EmailMessage
     │
     │ (1:1)
     ▼
ExtractedProposal (1) ──── (1) GeneratedProposal
```

### Table Details

**EmailThread** — Stores the complete email conversation
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique identifier |
| conversation_id | VARCHAR (unique) | Thread identifier from source |
| subject | TEXT | Email subject line |
| participants | JSON | Array of {name, email, role} |
| raw_messages | JSON | Original message data as-is |
| flattened_thread | TEXT | Chronological plain text for AI |
| created_at | DATETIME | Upload timestamp |

**EmailMessage** — Individual emails within a thread
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique identifier |
| thread | FK → EmailThread | Parent thread |
| message_id | VARCHAR | Original message ID |
| sender_name | VARCHAR | Sender display name |
| sender_email | EMAIL | Sender email address |
| recipients | JSON | To + CC recipients |
| timestamp | DATETIME | When email was sent |
| raw_body | TEXT | Original email body |
| clean_body | TEXT | Stripped of quoted history |

**ExtractedProposal** — AI-extracted commercial terms
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique identifier |
| thread | FK → EmailThread (1:1) | Source thread |
| raw_extraction | JSON | Complete Claude response |
| parties | JSON | Client, vendor, concertiv contacts |
| product | JSON | Product details |
| pricing | JSON | Pricing with history |
| license_terms | JSON | Duration, seats, renewal |
| sla_terms | JSON | Uptime, support tier |
| special_conditions | JSON Array | Special terms |
| ambiguities | JSON Array | Flagged issues |
| confidence | VARCHAR | high / medium / low |
| acceptance_signal | TEXT | Quote showing agreement |
| extraction_status | VARCHAR | pending / completed / failed |
| extracted_at | DATETIME | Extraction timestamp |

**GeneratedProposal** — Final proposal documents
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique identifier |
| extracted_proposal | FK → ExtractedProposal (1:1) | Source extraction |
| html_content | TEXT | Rendered HTML proposal |
| pdf_file | FILE | Generated PDF document |
| generated_at | DATETIME | Generation timestamp |
| is_approved | BOOLEAN | Human approval flag |

---

## 5. API Specification

| Method | Endpoint | Request | Response | Purpose |
|--------|----------|---------|----------|---------|
| POST | `/api/threads/upload/` | Multipart file OR JSON body | 201: Thread + Messages | Upload email thread |
| GET | `/api/threads/` | — | 200: Array of threads | List all threads |
| GET | `/api/threads/{id}/` | — | 200: Thread + messages | Thread detail |
| POST | `/api/threads/{id}/analyze/` | — | 200: {proposal_id, extraction} | Trigger AI extraction |
| GET | `/api/proposals/{id}/` | — | 200: Extracted proposal | Get proposal draft |
| PATCH | `/api/proposals/{id}/` | Partial JSON update | 200: Updated proposal | Edit extracted fields |
| POST | `/api/proposals/{id}/generate/` | — | 200: {html_content} | Generate PDF |
| GET | `/api/proposals/{id}/download/` | — | 200: PDF blob | Download PDF file |

---

## 6. AI Extraction Engine

### Processing Pipeline

```
Flattened Thread Text
        │
        ▼
┌─────────────────────────┐
│  1. PROMPT CONSTRUCTION │  Combine system prompt + thread text
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  2. CLAUDE API CALL     │  Model: claude-sonnet-4 (or opus-4 for higher quality)
│                         │  Max tokens: 4,096
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  3. RESPONSE PARSING    │  Strip markdown fences (```json)
│     (parser.py)         │  Parse JSON
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  4. DATA NORMALIZATION  │  Dates → ISO 8601 (2025-03-01)
│     (parser.py)         │  Prices → numeric ($20,500 → 20500)
│                         │  Integers → int ("18" → 18)
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  5. SCHEMA VALIDATION   │  Required sections present?
│     (validator.py)      │  Numeric fields valid?
│                         │  Confidence value valid?
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│  6. CONFIDENCE ADJUST   │  Ambiguities + high → medium
│     (validator.py)      │  No acceptance signal → low
│                         │  No unit price → low
└───────────┬─────────────┘
            ▼
      Validated Extraction Dict
```

### Cost Estimate (Real API Usage)

| Model | Input Cost | Output Cost | Per Thread (est.) | 100 Threads/Month |
|-------|-----------|-------------|-------------------|-------------------|
| claude-sonnet-4 | $3/1M tokens | $15/1M tokens | ~$0.03 | ~$3.00 |
| claude-opus-4 | $15/1M tokens | $75/1M tokens | ~$0.15 | ~$15.00 |

**Recommendation:** Use Sonnet for standard deals, Opus for complex multi-stakeholder negotiations.

---

## 7. Production Integration: Outlook + Microsoft Graph

### The Challenge

In production, email threads come from Outlook (Concertiv mail accounts), not JSON files. We need to:
1. Connect to Outlook mailboxes
2. Identify negotiation threads
3. Extract email data in real-time or on-demand
4. Convert Outlook email format → our JSON schema

### Solution: Microsoft Graph API

Microsoft Graph API provides programmatic access to Outlook emails in Microsoft 365 / Office 365.

### Integration Architecture

```
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│   Outlook        │     │  Microsoft Graph     │     │  Concertiv       │
│   Mailbox        │────→│  API                 │────→│  Backend         │
│                  │     │                      │     │                  │
│  @concertiv.com  │     │  GET /messages       │     │  Graph Client    │
│  Inbox/Sent      │     │  GET /conversations  │     │  → JSON → DB    │
│  Negotiations    │     │  Webhooks            │     │  → Claude → PDF │
└──────────────────┘     └─────────────────────┘     └──────────────────┘
```

### How It Works (3 Approaches)

#### Approach A: On-Demand Pull (Recommended for Phase 1)

User pastes a conversation ID or selects from a list, and the system fetches the thread from Outlook.

```
1. User clicks "Fetch from Outlook" in the UI
2. Backend calls Microsoft Graph API:
   GET https://graph.microsoft.com/v1.0/me/messages
       ?$filter=conversationId eq '{id}'
       &$orderby=receivedDateTime
       &$select=id,subject,from,toRecipients,ccRecipients,
                receivedDateTime,body,conversationId
3. Backend transforms Graph response → our JSON schema
4. Proceeds with normal extraction pipeline
```

**Graph API Response → Our Schema Mapping:**

```python
# Microsoft Graph email format:
{
    "id": "AAMkAGI2...",
    "conversationId": "AAQkAGI2...",
    "subject": "Re: Bloomberg Terminal Renewal",
    "from": {
        "emailAddress": {"name": "Sarah Chen", "address": "sarah@acme.com"}
    },
    "toRecipients": [
        {"emailAddress": {"name": "John Doe", "address": "john@concertiv.com"}}
    ],
    "receivedDateTime": "2025-02-10T09:15:00Z",
    "body": {"contentType": "html", "content": "<html>...email body...</html>"}
}

# Maps to our schema:
{
    "message_id": "AAMkAGI2...",        # from Graph 'id'
    "from": {"name": "Sarah Chen", "email": "sarah@acme.com"},
    "to": [{"name": "John Doe", "email": "john@concertiv.com"}],
    "timestamp": "2025-02-10T09:15:00Z", # from 'receivedDateTime'
    "body": "...stripped HTML to text..." # from 'body.content' (HTML → text)
}
```

#### Approach B: Webhook-Based Auto-Detect (Phase 2)

Microsoft Graph can notify our system when new emails arrive matching certain criteria.

```
1. Register webhook subscription:
   POST https://graph.microsoft.com/v1.0/subscriptions
   {
     "changeType": "created",
     "notificationUrl": "https://concertiv-app.com/api/webhooks/outlook/",
     "resource": "me/messages",
     "expirationDateTime": "2025-03-01T00:00:00Z"
   }

2. When new email arrives → Graph sends POST to our webhook
3. Backend checks if email is part of a negotiation thread
4. If yes → auto-fetch full thread → queue for extraction
5. Notify Concertiv user: "New negotiation update detected"
```

#### Approach C: Shared Mailbox Monitoring (Phase 3)

Monitor a shared mailbox (e.g., negotiations@concertiv.com) that all deal emails are CC'd to.

```
GET https://graph.microsoft.com/v1.0/users/{shared-mailbox-id}/messages
    ?$filter=receivedDateTime ge {last_check}
```

### Microsoft Graph Setup Requirements

| Requirement | Details |
|-------------|---------|
| **Azure AD App Registration** | Register app in Azure Portal → App Registrations |
| **API Permissions** | `Mail.Read`, `Mail.ReadBasic`, `User.Read` (delegated or application) |
| **Authentication** | OAuth 2.0 with MSAL (Microsoft Authentication Library) |
| **Admin Consent** | Required for application-level (daemon) access to mailboxes |
| **Client Credentials** | Client ID + Client Secret or Certificate |

### New Backend Components Needed

```
backend/
├── outlook/                        # NEW Django app
│   ├── graph_client.py             # Microsoft Graph API client
│   │   ├── authenticate()          # OAuth token management
│   │   ├── list_conversations()    # Search mailbox for threads
│   │   ├── fetch_thread()          # Get all messages in a conversation
│   │   └── transform_to_schema()   # Graph format → our JSON schema
│   │
│   ├── html_cleaner.py             # Convert HTML email bodies to plain text
│   │   ├── strip_signatures()      # Remove email signatures
│   │   ├── strip_quoted_replies()  # Remove "On Feb 10, X wrote:" blocks
│   │   └── clean_html_to_text()    # HTML tags → readable text
│   │
│   ├── views.py                    # New API endpoints
│   │   ├── list_outlook_threads()  # Browse Outlook conversations
│   │   ├── fetch_and_ingest()      # Pull thread from Outlook → DB
│   │   └── webhook_receiver()      # Handle Graph notifications
│   │
│   └── models.py
│       └── OutlookSync             # Track sync state per conversation
│           ├── conversation_id
│           ├── last_synced_at
│           └── auto_extract (bool)
│
├── config/
│   └── settings.py                 # Add: GRAPH_CLIENT_ID, GRAPH_TENANT_ID, etc.
│
└── .env                            # Add: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, etc.
```

### New API Endpoints (Production)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/outlook/threads/` | List recent Outlook conversations |
| GET | `/api/outlook/threads/?search=bloomberg` | Search Outlook by keyword |
| POST | `/api/outlook/threads/{conv_id}/fetch/` | Fetch from Outlook → ingest → DB |
| POST | `/api/outlook/webhooks/` | Receive Graph change notifications |

### New Frontend Screen (Production)

```
┌──────────────────────────────────────────────────┐
│  CONCERTIV Proposal Generator                    │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌─ Tab: Upload JSON ─┬─ Tab: Outlook Inbox ──┐ │
│  │                     │ [ACTIVE]              │ │
│  └─────────────────────┴───────────────────────┘ │
│                                                  │
│  Search: [bloomberg________________] [Search]    │
│                                                  │
│  Recent Negotiation Threads from Outlook:        │
│  ┌──────────────────────────────────────────┐    │
│  │ ★ Bloomberg Terminal - Acme Capital      │    │
│  │   Last email: 2 hours ago | 7 messages   │    │
│  │   [Fetch & Analyze]                      │    │
│  ├──────────────────────────────────────────┤    │
│  │   Refinitiv Data Feed - Meridian AM      │    │
│  │   Last email: 1 day ago | 12 messages    │    │
│  │   [Fetch & Analyze]                      │    │
│  ├──────────────────────────────────────────┤    │
│  │   FactSet Terminal - Zenith Capital      │    │
│  │   Last email: 3 days ago | 9 messages    │    │
│  │   [Fetch & Analyze]                      │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

---

## 8. Production Architecture (Target State)

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Outlook    │   │   Concertiv  │   │   Manager    │
│   Mailbox    │   │   Staff      │   │   Review     │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       │           ┌──────▼───────┐          │
       │           │  React App   │◄─────────┘
       │           │  (Hosted)    │
       │           └──────┬───────┘
       │                  │
       │           ┌──────▼───────┐
       │    ┌──────│  Django API  │──────┐
       │    │      │  (Hosted)    │      │
       │    │      └──────┬───────┘      │
       │    │             │              │
       ▼    ▼             ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ MS Graph API │ │ Claude API   │ │ PostgreSQL   │
│ (Outlook)    │ │ (Anthropic)  │ │ (Database)   │
└──────────────┘ └──────────────┘ └──────────────┘
                                         │
                                  ┌──────▼───────┐
                                  │ AWS S3 /     │
                                  │ Azure Blob   │
                                  │ (PDF Storage)│
                                  └──────────────┘

New Production Components:
─────────────────────────
• Authentication: Azure AD SSO (Concertiv staff only)
• Task Queue: Celery + Redis (async extraction for large threads)
• Database: PostgreSQL (from SQLite)
• File Storage: S3 or Azure Blob (from local filesystem)
• Hosting: Azure App Service or AWS (close to MS Graph)
• Monitoring: Sentry (errors), Datadog (performance)
• Caching: Redis (Outlook API responses)
```

---

## 9. Security & Compliance Considerations

| Area | POC (Current) | Production (Required) |
|------|---------------|----------------------|
| **Authentication** | None | Azure AD SSO, role-based access |
| **Email Data** | Dummy JSON files | Real client emails — encrypt at rest |
| **API Keys** | .env file | Azure Key Vault / AWS Secrets Manager |
| **Data Retention** | Indefinite | Policy-based retention + deletion |
| **Audit Trail** | None | Log all extractions, edits, downloads |
| **PII Handling** | Not addressed | Mask PII in logs, GDPR compliance |
| **Network** | localhost only | HTTPS, VPN, IP whitelisting |
| **Claude API** | Data sent to Anthropic | Review Anthropic data policy, consider private deployment |

**Important:** Anthropic's API data policy states they do not train on API inputs. However, for sensitive financial negotiations, confirm this meets Concertiv's data handling requirements.

---

## 10. Migration Plan: POC to Production

### Phase 1: Internal Pilot (Weeks 1-3)
- [ ] Deploy to internal server (Azure App Service)
- [ ] Switch SQLite → PostgreSQL
- [ ] Add Azure AD authentication (Concertiv staff only)
- [ ] Register Azure AD app for Microsoft Graph
- [ ] Build Outlook integration (on-demand pull)
- [ ] Add HTML email body → plain text conversion
- [ ] Test with 5-10 real negotiation threads
- [ ] Enable real Claude API ($5-15/month estimated)

### Phase 2: Team Rollout (Weeks 4-6)
- [ ] Add Celery + Redis for async extraction
- [ ] Add webhook-based auto-detection of new negotiations
- [ ] Build "Outlook Inbox" tab in frontend
- [ ] Add user roles (viewer, editor, admin)
- [ ] Add audit logging (who extracted, edited, downloaded)
- [ ] PDF storage on Azure Blob / S3
- [ ] Monitoring and alerting (Sentry, Datadog)

### Phase 3: Full Production (Weeks 7-10)
- [ ] Shared mailbox monitoring (negotiations@concertiv.com)
- [ ] Auto-extraction on thread completion detection
- [ ] Dashboard: deal pipeline, extraction stats, confidence trends
- [ ] Email notifications to account managers
- [ ] Integration with CRM (Salesforce / HubSpot)
- [ ] Batch processing for historical threads
- [ ] Performance optimization and caching

### Estimated Effort

| Phase | Scope | Estimated Effort |
|-------|-------|-----------------|
| Phase 1 | Internal pilot + Outlook integration | 2-3 weeks, 1-2 engineers |
| Phase 2 | Team rollout + async + auto-detect | 2-3 weeks, 2 engineers |
| Phase 3 | Full production + integrations | 3-4 weeks, 2-3 engineers |

---

*Document generated for Concertiv Engineering*
*February 2026*
