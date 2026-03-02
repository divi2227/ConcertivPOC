/**
 * Extracts searchable terms from proposal data for highlighting in email bodies.
 * Returns an array of { term, label } objects sorted longest-first to avoid
 * partial matches when building the highlight regex.
 */
export function getHighlightTerms(proposal) {
  if (!proposal) return [];

  const terms = [];

  const add = (value, label) => {
    if (value == null || value === '') return;
    const s = String(value).trim();
    if (s.length < 2) return;
    terms.push({ term: s, label });
  };

  // Pricing values — search for both raw numbers and formatted variants
  const pricing = proposal.pricing || {};
  if (pricing.unit_price != null) {
    const p = pricing.unit_price;
    add(`$${Number(p).toLocaleString()}`, 'Unit Price');
    add(`$${p}`, 'Unit Price');
    add(`${Number(p).toLocaleString()}`, 'Unit Price');
  }
  if (pricing.total_annual_value != null) {
    const v = pricing.total_annual_value;
    add(`$${Number(v).toLocaleString()}`, 'Annual Value');
    add(`${Number(v).toLocaleString()}`, 'Annual Value');
  }
  if (pricing.total_contract_value != null) {
    const v = pricing.total_contract_value;
    add(`$${Number(v).toLocaleString()}`, 'Contract Value');
    add(`${Number(v).toLocaleString()}`, 'Contract Value');
  }
  if (pricing.quantity != null) {
    add(`${pricing.quantity} seats`, 'Quantity');
    add(`${pricing.quantity} seat`, 'Quantity');
  }
  if (pricing.price_escalation_cap && pricing.price_escalation_cap !== 'Not specified' && pricing.price_escalation_cap !== 'Not discussed') {
    add(pricing.price_escalation_cap, 'Price Cap');
  }
  // Price history rounds
  (pricing.price_history || []).forEach((h) => {
    if (h.unit_price != null) {
      add(`$${Number(h.unit_price).toLocaleString()}`, `Round ${h.round} Price`);
      add(`$${h.unit_price}`, `Round ${h.round} Price`);
    }
  });

  // License terms
  const terms_ = proposal.license_terms || {};
  if (terms_.term_years != null) {
    add(`${terms_.term_years}-year`, 'Term');
    add(`${terms_.term_years} year`, 'Term');
  }
  if (terms_.seat_count != null) {
    add(`${terms_.seat_count} seats`, 'Seats');
    add(`${terms_.seat_count} seat`, 'Seats');
  }
  if (terms_.start_date) add(terms_.start_date, 'Start Date');
  if (terms_.end_date) add(terms_.end_date, 'End Date');

  // SLA
  const sla = proposal.sla_terms || {};
  if (sla.uptime_commitment && sla.uptime_commitment !== '') {
    add(sla.uptime_commitment, 'SLA Uptime');
  }

  // Acceptance signal
  if (proposal.acceptance_signal) {
    add(proposal.acceptance_signal, 'Acceptance Signal');
  }

  // Deduplicate by term (case-insensitive), keep longest first
  const seen = new Set();
  const unique = [];
  // Sort longest first so longer matches take priority
  terms.sort((a, b) => b.term.length - a.term.length);
  for (const t of terms) {
    const key = t.term.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(t);
    }
  }

  return unique;
}

/**
 * Escapes a string for use in a RegExp.
 */
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Splits text into segments: plain text and highlighted matches.
 * Returns an array of { text, highlight, label } objects.
 */
export function highlightText(text, highlightTerms) {
  if (!text || !highlightTerms || highlightTerms.length === 0) {
    return [{ text, highlight: false }];
  }

  // Build a single regex with alternation, longest terms first (already sorted)
  const patterns = highlightTerms.map(t => escapeRegex(t.term));
  const regex = new RegExp(`(${patterns.join('|')})`, 'gi');

  // Build a lookup from lowercase term → label
  const labelMap = {};
  for (const t of highlightTerms) {
    labelMap[t.term.toLowerCase()] = t.label;
  }

  const segments = [];
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ text: text.slice(lastIndex, match.index), highlight: false });
    }
    segments.push({
      text: match[0],
      highlight: true,
      label: labelMap[match[0].toLowerCase()] || '',
    });
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    segments.push({ text: text.slice(lastIndex), highlight: false });
  }

  return segments;
}
