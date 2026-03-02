import markdown
from weasyprint import HTML

md_content = """
# AI Extraction Engine — Step-by-Step Technical Reference

**System:** Concertiv Intelligent Proposal Generation
**Component:** extraction/ (Django app)
**Date:** February 2026 | **Confidential**

---

## Overview

When a user clicks "Analyze" on an uploaded email thread, the extraction engine processes it through a 7-step pipeline that reads the raw emails, sends them to Claude AI, and produces a structured, validated JSON extraction of all commercial terms.

---

## Step 1: Thread Flattening

**File:** `threads/services.py` — `ThreadIngestionService.flatten_thread()`

The raw email messages (stored individually in the database) get combined into one chronological text block. This is what Claude actually reads:

```
--- Message 1 of 7 [msg-001] ---
From: Sarah Chen <sarah@acmecapital.com> (Client)
To: John Doe <john@concertiv.com>
Date: 2025-02-10T09:15:00Z
Subject: Bloomberg Terminal License Renewal

Hi John, we're looking to renew our Bloomberg terminals...

--- Message 2 of 7 [msg-002] ---
From: John Doe <john@concertiv.com> (Concertiv)
To: Mike Torres <mike@bloomberg.net>
...
```

Each sender is labeled with their role (Client / Vendor / Concertiv) so Claude understands who is who in the negotiation.

---

## Step 2: Prompt Construction

**File:** `extraction/prompt_templates.py` — `EXTRACTION_PROMPT`

The flattened text gets injected into a carefully engineered prompt that tells Claude:

- **Who it is:** "You are an expert commercial analyst for Concertiv"
- **What to do:** Extract the FINAL agreed commercial terms
- **Key rules:**
    - Focus on final state, not intermediate offers
    - Look for acceptance signals ("agreed", "that works", "please proceed")
    - Look for implied acceptance (next steps without counter-offer)
    - Track price evolution across all rounds
    - Return ONLY valid JSON
- **Exact output schema:** The 12-field JSON structure (parties, pricing, license_terms, etc.)

The prompt ends with the full flattened thread text.

---

## Step 3: Claude API Call

**File:** `extraction/claude_client.py` — `ClaudeExtractionClient.extract()`

```python
response = self.client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}]
)
raw_text = response.content[0].text
```

Claude reads the entire conversation, understands the negotiation dynamics, identifies who proposed what, tracks counter-offers, finds the final agreement, and returns a JSON blob with all extracted fields.

---

## Step 4: Response Parsing

**File:** `extraction/parser.py` — `ExtractionParser.parse_response()`

Claude's raw text response goes through 3 cleanup steps:

### a) Strip Markdown Fences
Claude sometimes wraps JSON in markdown code blocks. The parser detects and removes this:

| Input | Output |
|-------|--------|
| ` ```json {"confidence": "high"} ``` ` | `{"confidence": "high"}` |

### b) Date Normalization
Converts human-readable dates to ISO 8601 format:

| Input | Output |
|-------|--------|
| "March 1, 2025" | "2025-03-01" |
| "Feb 28 2027" | "2027-02-28" |

### c) Numeric Coercion
Converts string numbers to actual numeric types:

| Input | Output | Field |
|-------|--------|-------|
| "$20,500" | 20500 | unit_price |
| "18" | 18 | quantity |
| "2" | 2 | term_years |

This also runs on every entry in the `price_history` array.

---

## Step 5: Schema Validation

**File:** `extraction/validator.py` — `ExtractionValidator.validate()`

Checks that the extraction is structurally valid:

| Check | Rule |
|-------|------|
| Required sections | parties, product, pricing, license_terms, confidence must exist |
| Confidence value | Must be "high", "medium", or "low" |
| Numeric pricing fields | unit_price, quantity, total_annual_value, total_contract_value must be numbers or null |
| Numeric license fields | term_years, seat_count must be numbers or null |

Returns `(is_valid, list_of_issues)`. If invalid, the extraction fails with an error message sent back to the frontend.

---

## Step 6: Confidence Adjustment

**File:** `extraction/validator.py` — `ExtractionValidator.adjust_confidence()`

Even if Claude says "high" confidence, the system applies business rules to override:

| Rule | Condition | Action |
|------|-----------|--------|
| Ambiguity check | Ambiguities list is non-empty AND confidence is "high" | Downgrade to **medium** |
| Acceptance check | No acceptance signal found (empty string) | Force to **low** |
| Price check | No unit_price extracted (null) | Force to **low** |
| Date check | No start_date AND no end_date AND confidence is "high" | Downgrade to **medium** |

This ensures the confidence rating is conservative — better to flag something for human review than to miss an issue.

---

## Step 7: Save to Database

**File:** `threads/views.py` — `analyze_thread()`

The validated, adjusted extraction dict gets saved to the `ExtractedProposal` table with each section in its own JSON column:

| Column | Source |
|--------|--------|
| raw_extraction | Full Claude response (backup) |
| parties | Client, vendor, concertiv contacts |
| pricing | Prices, quantities, history |
| license_terms | Duration, seats, renewal |
| sla_terms | Uptime, support tier |
| special_conditions | Caps, pilots, MFN clauses |
| ambiguities | Flagged unresolved items |
| confidence | Adjusted confidence level |
| acceptance_signal | Exact acceptance quote |
| extraction_status | "completed" |

The extraction is then returned to the frontend for human review and editing.

---

## Full Pipeline Diagram

```
Raw emails in DB
      |
      v
  Step 1: Flatten (chronological text with roles)
      |
      v
  Step 2: Build prompt (instructions + schema + thread)
      |
      v
  Step 3: Claude API call (AI reads and extracts)
      |
      v
  Step 4: Parse response (strip fences, parse JSON)
      |
      v
  Step 5: Normalize (dates to ISO, prices to numbers)
      |
      v
  Step 6: Validate (required fields, correct types)
      |
      v
  Step 7: Adjust confidence (apply business rules)
      |
      v
  Save to ExtractedProposal table
      |
      v
  Return to frontend for human review
```

---

## Cost Estimate (Real API Usage)

| Model | Input Cost | Output Cost | Per Thread (est.) | 100 Threads/Month |
|-------|-----------|-------------|-------------------|-------------------|
| claude-sonnet-4 | $3 / 1M tokens | $15 / 1M tokens | ~$0.03 | ~$3.00 |
| claude-opus-4 | $15 / 1M tokens | $75 / 1M tokens | ~$0.15 | ~$15.00 |

**Recommendation:** Use Sonnet for standard deals, Opus for complex multi-stakeholder negotiations.

---

## Files Summary

| File | Purpose |
|------|---------|
| `extraction/claude_client.py` | Orchestrates the full pipeline: prompt -> API call -> parse -> validate -> adjust |
| `extraction/prompt_templates.py` | Contains the EXTRACTION_PROMPT constant with instructions and schema |
| `extraction/parser.py` | Strips markdown fences, normalizes dates, coerces numeric fields |
| `extraction/validator.py` | Schema validation + confidence adjustment business rules |
| `extraction/mock_responses.py` | Mock responses for testing without API credits |

---

*Concertiv Engineering — AI Extraction Engine Reference*
*February 2026*
"""

html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

full_html = (
    '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
    '@page { size: A4; margin: 2cm 2.5cm; @bottom-center { content: counter(page); font-size: 10px; color: #999; } }'
    'body { font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.6; color: #1a1a1a; }'
    'h1 { color: #1B2A4A; font-size: 22pt; border-bottom: 3px solid #C9A84C; padding-bottom: 10px; margin-top: 30px; }'
    'h2 { color: #1B2A4A; font-size: 16pt; margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 6px; page-break-after: avoid; }'
    'h3 { color: #2a4a7a; font-size: 13pt; margin-top: 20px; page-break-after: avoid; }'
    'p { margin: 8px 0; }'
    'table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 10pt; page-break-inside: avoid; }'
    'th { background: #1B2A4A; color: white; padding: 8px 12px; text-align: left; font-weight: 600; font-size: 9.5pt; }'
    'td { padding: 7px 12px; border-bottom: 1px solid #e0e0e0; vertical-align: top; }'
    'tr:nth-child(even) td { background: #f8f9fa; }'
    'code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; font-size: 9.5pt; color: #c7254e; }'
    'pre { background: #1B2A4A; color: #e8e8e8; padding: 14px 18px; border-radius: 6px; font-family: Consolas, monospace; font-size: 8.5pt; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; margin: 12px 0; }'
    'pre code { background: none; color: #e8e8e8; padding: 0; font-size: 8.5pt; }'
    'ul, ol { margin: 8px 0; padding-left: 24px; }'
    'li { margin: 4px 0; }'
    'strong { color: #1B2A4A; }'
    'hr { border: none; border-top: 2px solid #C9A84C; margin: 30px 0; }'
    '</style></head><body>'
    + html_body
    + '</body></html>'
)

output_path = '/mnt/c/Users/DivyangSharma/concertiv-poc/AI_Extraction_Engine_Reference.pdf'
HTML(string=full_html).write_pdf(output_path)
print(f'PDF generated: {output_path}')
