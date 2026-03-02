class ExtractionValidator:
    REQUIRED_SECTIONS = ['parties', 'product', 'pricing', 'license_terms', 'confidence']
    VALID_CONFIDENCE = ['high', 'medium', 'low']

    def validate(self, extraction: dict) -> tuple:
        """Validate extraction against schema. Returns (is_valid, issues)."""
        issues = []

        # Check required sections exist
        for section in self.REQUIRED_SECTIONS:
            if section not in extraction:
                issues.append(f"Missing required section: {section}")

        # Validate confidence value
        confidence = extraction.get('confidence', '')
        if confidence not in self.VALID_CONFIDENCE:
            issues.append(f"Invalid confidence value: {confidence}")

        # Validate numeric pricing fields
        pricing = extraction.get('pricing', {})
        for field in ['unit_price', 'quantity', 'total_annual_value', 'total_contract_value']:
            value = pricing.get(field)
            if value is not None and not isinstance(value, (int, float)):
                issues.append(f"pricing.{field} must be numeric or null, got {type(value).__name__}")

        # Validate license_terms numeric fields
        license_terms = extraction.get('license_terms', {})
        for field in ['term_years', 'seat_count']:
            value = license_terms.get(field)
            if value is not None and not isinstance(value, (int, float)):
                issues.append(f"license_terms.{field} must be numeric or null, got {type(value).__name__}")

        return (len(issues) == 0, issues)

    def adjust_confidence(self, extraction: dict) -> dict:
        """Apply confidence adjustment rules."""
        ambiguities = extraction.get('ambiguities', [])
        confidence = extraction.get('confidence', 'low')
        acceptance_signal = extraction.get('acceptance_signal', '')
        pricing = extraction.get('pricing', {})
        license_terms = extraction.get('license_terms', {})

        # Rule: If ambiguities exist and confidence is high, downgrade to medium
        if ambiguities and confidence == 'high':
            extraction['confidence'] = 'medium'

        # Rule: Low confidence if no acceptance signal
        if not acceptance_signal:
            extraction['confidence'] = 'low'

        # Rule: Low confidence if pricing has no unit_price
        if pricing.get('unit_price') is None:
            extraction['confidence'] = 'low'

        # Rule: Low confidence if term dates missing
        if not license_terms.get('start_date') and not license_terms.get('end_date'):
            if extraction['confidence'] == 'high':
                extraction['confidence'] = 'medium'

        return extraction
