EXTRACTION_PROMPT = """You are an expert commercial analyst for Concertiv, a procurement intermediary in the financial services industry.

Below is an email thread between a Client, a Vendor, and Concertiv.
Your task is to analyze the full thread and extract the FINAL agreed commercial terms.

IMPORTANT RULES:
1. Focus on the FINAL agreed state, not intermediate proposals or counteroffers.
2. Look for explicit acceptance signals: "agreed", "that works", "confirmed", "please proceed", "sounds good", "we'll take it".
3. Look for implied acceptance: next steps discussed without any counter-offer following.
4. If negotiation is unresolved, set confidence to "low" and explain in ambiguities.
5. Track price evolution across rounds and summarize in negotiation_summary.
6. Return ONLY valid JSON. No preamble, no explanation outside the JSON.

OUTPUT SCHEMA:
{
  "parties": {
    "client_name": "",
    "client_contact": {"name": "", "email": ""},
    "vendor_name": "",
    "vendor_contact": {"name": "", "email": ""},
    "concertiv_contact": {"name": "", "email": ""}
  },
  "product": {
    "name": "",
    "description": "",
    "inclusions": [],
    "exclusions": []
  },
  "pricing": {
    "unit": "",
    "unit_price": null,
    "quantity": null,
    "total_annual_value": null,
    "total_contract_value": null,
    "currency": "USD",
    "price_escalation_cap": "",
    "negotiation_summary": "",
    "price_history": [
      {"round": 1, "proposed_by": "", "unit_price": null, "notes": ""}
    ]
  },
  "license_terms": {
    "term_years": null,
    "start_date": "",
    "end_date": "",
    "seat_count": null,
    "usage_type": "",
    "renewal_type": "",
    "usage_restrictions": []
  },
  "sla_terms": {
    "uptime_commitment": "",
    "support_tier": "",
    "notes": ""
  },
  "special_conditions": [],
  "ambiguities": [],
  "confidence": "high|medium|low",
  "acceptance_signal": "",
  "acceptance_message_id": ""
}

EMAIL THREAD:
{flattened_thread}"""
