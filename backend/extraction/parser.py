import json
import re
from dateutil import parser as dateutil_parser


class ExtractionParser:
    def parse_response(self, raw_text: str) -> dict:
        """Parse Claude's response, handling markdown fences and cleanup."""
        cleaned = self._strip_markdown_fences(raw_text)
        data = json.loads(cleaned)
        data = self._normalize_dates(data)
        data = self._coerce_numeric_fields(data)
        return data

    def _strip_markdown_fences(self, text: str) -> str:
        """Remove ```json ... ``` wrappers if present."""
        text = text.strip()
        # Remove markdown code fences
        pattern = r'^```(?:json)?\s*\n?(.*?)\n?\s*```$'
        match = re.match(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    def _normalize_dates(self, data: dict) -> dict:
        """Normalize date strings to ISO 8601 format."""
        license_terms = data.get('license_terms', {})
        for field in ['start_date', 'end_date']:
            value = license_terms.get(field, '')
            if value and isinstance(value, str):
                try:
                    parsed = dateutil_parser.parse(value)
                    license_terms[field] = parsed.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    pass  # Keep original if unparseable
        data['license_terms'] = license_terms
        return data

    def _coerce_numeric_fields(self, data: dict) -> dict:
        """Ensure numeric fields are proper numbers or None."""
        pricing = data.get('pricing', {})
        numeric_fields = ['unit_price', 'quantity', 'total_annual_value', 'total_contract_value']
        for field in numeric_fields:
            value = pricing.get(field)
            if value is not None and not isinstance(value, (int, float)):
                try:
                    # Handle string numbers like "$20,500" or "20500"
                    cleaned = str(value).replace('$', '').replace(',', '').strip()
                    pricing[field] = float(cleaned) if '.' in cleaned else int(cleaned)
                except (ValueError, TypeError):
                    pricing[field] = None
        data['pricing'] = pricing

        # Coerce license_terms numeric fields
        license_terms = data.get('license_terms', {})
        for field in ['term_years', 'seat_count']:
            value = license_terms.get(field)
            if value is not None and not isinstance(value, (int, float)):
                try:
                    license_terms[field] = int(str(value).strip())
                except (ValueError, TypeError):
                    license_terms[field] = None
        data['license_terms'] = license_terms

        # Coerce price_history entries
        for entry in pricing.get('price_history', []):
            if 'unit_price' in entry and entry['unit_price'] is not None:
                if not isinstance(entry['unit_price'], (int, float)):
                    try:
                        cleaned = str(entry['unit_price']).replace('$', '').replace(',', '').strip()
                        entry['unit_price'] = float(cleaned) if '.' in cleaned else int(cleaned)
                    except (ValueError, TypeError):
                        entry['unit_price'] = None

        return data
