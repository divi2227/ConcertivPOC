"""Mock extraction responses for testing without Claude API credits."""

MOCK_THREAD_001 = {
    "parties": {
        "client_name": "Acme Capital",
        "client_contact": {"name": "Sarah Chen", "email": "sarah.chen@acmecapital.com"},
        "vendor_name": "Bloomberg LP",
        "vendor_contact": {"name": "Mike Torres", "email": "mike.torres@bloomberg.net"},
        "concertiv_contact": {"name": "John Doe", "email": "john.doe@concertiv.com"}
    },
    "product": {
        "name": "Bloomberg Terminal",
        "description": "Bloomberg Terminal professional license for financial data, analytics, and trading tools",
        "inclusions": ["Real-time market data", "Bloomberg Analytics", "Trading tools", "News feed"],
        "exclusions": ["Custom API integrations", "Third-party data overlays"]
    },
    "pricing": {
        "unit": "Per Seat/Year",
        "unit_price": 20500,
        "quantity": 18,
        "total_annual_value": 369000,
        "total_contract_value": 738000,
        "currency": "USD",
        "price_escalation_cap": "3% Year 2 cap",
        "negotiation_summary": "Started at $22,000/seat (current rate). Bloomberg offered $21,500, client countered at $20,000 with 3% cap. Final agreement at $20,500/seat with 3% Year 2 escalation cap.",
        "price_history": [
            {"round": 1, "proposed_by": "Bloomberg LP", "unit_price": 21500, "notes": "Initial renewal offer, down from current $22,000"},
            {"round": 2, "proposed_by": "Acme Capital", "unit_price": 20000, "notes": "Counter-offer with 3% Year 2 cap request"},
            {"round": 3, "proposed_by": "Bloomberg LP", "unit_price": 20500, "notes": "Final offer: $20,500 with 3% cap accepted"}
        ]
    },
    "license_terms": {
        "term_years": 2,
        "start_date": "2025-03-01",
        "end_date": "2027-02-28",
        "seat_count": 18,
        "usage_type": "Named user license",
        "renewal_type": "Standard renewal",
        "usage_restrictions": []
    },
    "sla_terms": {
        "uptime_commitment": "99.9%",
        "support_tier": "Standard",
        "notes": "Standard Bloomberg support included"
    },
    "special_conditions": [
        "Year 2 price escalation capped at 3%",
        "Same seat count maintained from previous contract"
    ],
    "ambiguities": [],
    "confidence": "high",
    "acceptance_signal": "That works for us. Please proceed with $20,500/seat, 18 seats, 2-year term with the 3% Year 2 cap.",
    "acceptance_message_id": "msg-007"
}

MOCK_THREAD_002 = {
    "parties": {
        "client_name": "Meridian Asset Management",
        "client_contact": {"name": "David Park", "email": "david.park@meridianam.com"},
        "vendor_name": "Refinitiv",
        "vendor_contact": {"name": "Rachel Adams", "email": "rachel.adams@refinitiv.com"},
        "concertiv_contact": {"name": "Priya Sharma", "email": "priya.sharma@concertiv.com"}
    },
    "product": {
        "name": "Refinitiv Eikon Data Feed",
        "description": "Enterprise-grade financial data feed with real-time market data, analytics, and research tools",
        "inclusions": ["Real-time data feed", "Eikon analytics platform", "Research tools", "Dedicated account manager"],
        "exclusions": ["Custom data integrations", "Historical data backfill beyond 5 years"]
    },
    "pricing": {
        "unit": "Per Seat/Year",
        "unit_price": 13500,
        "quantity": 25,
        "total_annual_value": 337500,
        "total_contract_value": 675000,
        "currency": "USD",
        "price_escalation_cap": "Not specified",
        "negotiation_summary": "Started at $15,000/seat. Client pushed for $12,000. Refinitiv offered $14,000 with 2-year commitment. After SLA negotiations (client wanted 99.9%, settled on 99.5% with dedicated account manager), final price agreed at $13,500/seat as compromise.",
        "price_history": [
            {"round": 1, "proposed_by": "Refinitiv", "unit_price": 15000, "notes": "Initial enterprise tier offer"},
            {"round": 2, "proposed_by": "Meridian Asset Management", "unit_price": 12000, "notes": "Client counter - budget constraints"},
            {"round": 3, "proposed_by": "Refinitiv", "unit_price": 14000, "notes": "Revised with 2-year commitment"},
            {"round": 4, "proposed_by": "Meridian Asset Management", "unit_price": 13000, "notes": "Counter with SLA requirements"},
            {"round": 5, "proposed_by": "Refinitiv", "unit_price": 13500, "notes": "Final compromise with dedicated account manager"}
        ]
    },
    "license_terms": {
        "term_years": 2,
        "start_date": "2025-04-01",
        "end_date": "2027-03-31",
        "seat_count": 25,
        "usage_type": "Enterprise license",
        "renewal_type": "Not explicitly specified",
        "usage_restrictions": ["Internal use only", "No redistribution of data"]
    },
    "sla_terms": {
        "uptime_commitment": "99.5%",
        "support_tier": "Premium",
        "notes": "Dedicated account manager included. Client originally requested 99.9% uptime but Refinitiv held firm at 99.5%."
    },
    "special_conditions": [
        "Dedicated account manager assigned",
        "Premium support tier included at no extra cost",
        "SLA settled at 99.5% after negotiation from 99.9% ask"
    ],
    "ambiguities": [
        "Acceptance is implied ('Let's get the paperwork started') rather than explicit agreement on price"
    ],
    "confidence": "medium",
    "acceptance_signal": "Let's get the paperwork started",
    "acceptance_message_id": "msg-013"
}

MOCK_THREAD_003 = {
    "parties": {
        "client_name": "Zenith Capital Partners",
        "client_contact": {"name": "James Liu", "email": "james.liu@zenithcap.com"},
        "vendor_name": "FactSet",
        "vendor_contact": {"name": "Amanda Foster", "email": "amanda.foster@factset.com"},
        "concertiv_contact": {"name": "Marcus Webb", "email": "marcus.webb@concertiv.com"}
    },
    "product": {
        "name": "FactSet Terminal",
        "description": "FactSet terminal access for financial research, analytics, and portfolio management",
        "inclusions": ["Terminal access", "Standard data packages", "Research tools"],
        "exclusions": ["Custom analytics modules", "API access"]
    },
    "pricing": {
        "unit": "Per Seat/Year",
        "unit_price": 16500,
        "quantity": 10,
        "total_annual_value": 165000,
        "total_contract_value": 330000,
        "currency": "USD",
        "price_escalation_cap": "Not discussed",
        "negotiation_summary": "FactSet proposed $18,000/seat for 12 seats. Client indicated budget max of $15,000 and uncertain headcount (10-12). FactSet revised to $16,500 with minimum 10 seats. Client has not explicitly accepted the $16,500 price point. Vendor moved to discussing implementation timeline without formal price acceptance.",
        "price_history": [
            {"round": 1, "proposed_by": "FactSet", "unit_price": 18000, "notes": "Initial offer for 12 seats, 3-year term"},
            {"round": 2, "proposed_by": "Zenith Capital Partners", "unit_price": 15000, "notes": "Budget constraint, seat count uncertain"},
            {"round": 3, "proposed_by": "FactSet", "unit_price": 16500, "notes": "Revised: minimum 10 seats, 2-year term, flex arrangement"}
        ]
    },
    "license_terms": {
        "term_years": 2,
        "start_date": "2025-04-01",
        "end_date": "2027-03-31",
        "seat_count": 10,
        "usage_type": "Named user",
        "renewal_type": "",
        "usage_restrictions": []
    },
    "sla_terms": {
        "uptime_commitment": "",
        "support_tier": "",
        "notes": "No SLA terms discussed in the thread"
    },
    "special_conditions": [
        "Flexible seat arrangement - can add seats at same rate",
        "Starting with 10 seats, potential expansion to 12 based on Q2 hiring"
    ],
    "ambiguities": [
        "No explicit price acceptance from client - vendor moved to implementation planning without formal agreement",
        "Exact seat count unclear: '10-12 depending on Q2 hiring'",
        "Renewal type not specified or discussed",
        "No SLA or support terms negotiated"
    ],
    "confidence": "low",
    "acceptance_signal": "",
    "acceptance_message_id": ""
}


def get_mock_extraction(flattened_thread: str) -> dict:
    """Return mock extraction based on thread content."""
    text = flattened_thread.lower()
    if 'bloomberg' in text or 'acme capital' in text or 'thread_001' in text:
        return MOCK_THREAD_001.copy()
    elif 'refinitiv' in text or 'meridian' in text or 'thread_002' in text:
        return MOCK_THREAD_002.copy()
    elif 'factset' in text or 'zenith' in text or 'thread_003' in text:
        return MOCK_THREAD_003.copy()
    # Default to thread_001 for unknown threads
    return MOCK_THREAD_001.copy()
