import json
from unittest.mock import patch, MagicMock

from django.test import TestCase

from extraction.parser import ExtractionParser
from extraction.validator import ExtractionValidator
from extraction.claude_client import ClaudeExtractionClient, ExtractionError
from extraction.models import ExtractedProposal
from threads.models import EmailThread
from threads.services import ThreadIngestionService


def _load_thread_json(filename):
    """Load a thread JSON fixture from data/threads/."""
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent / 'data' / 'threads' / filename
    with open(path) as f:
        return json.load(f)


def _make_valid_extraction(**overrides):
    """Return a minimal valid extraction dict."""
    base = {
        'parties': {
            'client_name': 'Acme Capital',
            'client_contact': {'name': 'Sarah Chen', 'email': 'sarah.chen@acmecapital.com'},
            'vendor_name': 'Bloomberg LP',
            'vendor_contact': {'name': 'Mike Torres', 'email': 'mike.torres@bloomberg.net'},
            'concertiv_contact': {'name': 'John Doe', 'email': 'john.doe@concertiv.com'},
        },
        'product': {
            'name': 'Bloomberg Terminal',
            'description': 'Terminal license',
            'inclusions': [],
            'exclusions': [],
        },
        'pricing': {
            'unit': 'seat/year',
            'unit_price': 20500,
            'quantity': 18,
            'total_annual_value': 369000,
            'total_contract_value': 738000,
            'currency': 'USD',
            'price_escalation_cap': '3% year 2',
            'negotiation_summary': 'Negotiated from $22,000 to $20,500',
            'price_history': [
                {'round': 1, 'proposed_by': 'vendor', 'unit_price': 21500, 'notes': 'Initial offer'},
            ],
        },
        'license_terms': {
            'term_years': 2,
            'start_date': '2025-03-01',
            'end_date': '2027-02-28',
            'seat_count': 18,
            'usage_type': 'named user',
            'renewal_type': 'renewal',
            'usage_restrictions': [],
        },
        'sla_terms': {'uptime_commitment': '', 'support_tier': '', 'notes': ''},
        'special_conditions': [],
        'ambiguities': [],
        'confidence': 'high',
        'acceptance_signal': 'That works for us. Please proceed.',
        'acceptance_message_id': 'msg-007',
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# ExtractionParser tests
# ---------------------------------------------------------------------------

class ExtractionParserTests(TestCase):
    def setUp(self):
        self.parser = ExtractionParser()

    def test_parse_plain_json(self):
        raw = json.dumps(_make_valid_extraction())
        result = self.parser.parse_response(raw)
        self.assertEqual(result['pricing']['unit_price'], 20500)

    def test_parse_markdown_fenced_json(self):
        raw = '```json\n' + json.dumps(_make_valid_extraction()) + '\n```'
        result = self.parser.parse_response(raw)
        self.assertEqual(result['confidence'], 'high')

    def test_parse_markdown_fenced_no_lang(self):
        raw = '```\n' + json.dumps(_make_valid_extraction()) + '\n```'
        result = self.parser.parse_response(raw)
        self.assertIn('parties', result)

    def test_date_normalization(self):
        extraction = _make_valid_extraction()
        extraction['license_terms']['start_date'] = 'March 1, 2025'
        extraction['license_terms']['end_date'] = 'Feb 28, 2027'
        raw = json.dumps(extraction)
        result = self.parser.parse_response(raw)
        self.assertEqual(result['license_terms']['start_date'], '2025-03-01')
        self.assertEqual(result['license_terms']['end_date'], '2027-02-28')

    def test_coerce_string_unit_price(self):
        extraction = _make_valid_extraction()
        extraction['pricing']['unit_price'] = '$20,500'
        raw = json.dumps(extraction)
        result = self.parser.parse_response(raw)
        self.assertEqual(result['pricing']['unit_price'], 20500)

    def test_coerce_string_quantity(self):
        extraction = _make_valid_extraction()
        extraction['pricing']['quantity'] = '18'
        raw = json.dumps(extraction)
        result = self.parser.parse_response(raw)
        self.assertEqual(result['pricing']['quantity'], 18)

    def test_coerce_price_history_entries(self):
        extraction = _make_valid_extraction()
        extraction['pricing']['price_history'] = [
            {'round': 1, 'proposed_by': 'vendor', 'unit_price': '$21,500', 'notes': ''}
        ]
        raw = json.dumps(extraction)
        result = self.parser.parse_response(raw)
        self.assertEqual(result['pricing']['price_history'][0]['unit_price'], 21500)

    def test_coerce_term_years_string(self):
        extraction = _make_valid_extraction()
        extraction['license_terms']['term_years'] = '2'
        raw = json.dumps(extraction)
        result = self.parser.parse_response(raw)
        self.assertEqual(result['license_terms']['term_years'], 2)

    def test_invalid_json_raises(self):
        with self.assertRaises(json.JSONDecodeError):
            self.parser.parse_response('not valid json at all')


# ---------------------------------------------------------------------------
# ExtractionValidator tests
# ---------------------------------------------------------------------------

class ExtractionValidatorTests(TestCase):
    def setUp(self):
        self.validator = ExtractionValidator()

    def test_valid_extraction_passes(self):
        is_valid, issues = self.validator.validate(_make_valid_extraction())
        self.assertTrue(is_valid)
        self.assertEqual(issues, [])

    def test_missing_required_section(self):
        extraction = _make_valid_extraction()
        del extraction['parties']
        is_valid, issues = self.validator.validate(extraction)
        self.assertFalse(is_valid)
        self.assertIn('Missing required section: parties', issues)

    def test_invalid_confidence_value(self):
        extraction = _make_valid_extraction(confidence='very_high')
        is_valid, issues = self.validator.validate(extraction)
        self.assertFalse(is_valid)
        self.assertTrue(any('confidence' in i for i in issues))

    def test_non_numeric_pricing_detected(self):
        extraction = _make_valid_extraction()
        extraction['pricing']['unit_price'] = 'expensive'
        is_valid, issues = self.validator.validate(extraction)
        self.assertFalse(is_valid)
        self.assertTrue(any('unit_price' in i for i in issues))

    def test_non_numeric_term_years_detected(self):
        extraction = _make_valid_extraction()
        extraction['license_terms']['term_years'] = 'two'
        is_valid, issues = self.validator.validate(extraction)
        self.assertFalse(is_valid)
        self.assertTrue(any('term_years' in i for i in issues))

    # ----- adjust_confidence tests -----

    def test_high_with_ambiguities_downgrades_to_medium(self):
        extraction = _make_valid_extraction(
            confidence='high',
            ambiguities=['seat count unclear'],
            acceptance_signal='agreed',
        )
        result = self.validator.adjust_confidence(extraction)
        self.assertEqual(result['confidence'], 'medium')

    def test_no_acceptance_signal_forces_low(self):
        extraction = _make_valid_extraction(acceptance_signal='')
        result = self.validator.adjust_confidence(extraction)
        self.assertEqual(result['confidence'], 'low')

    def test_no_unit_price_forces_low(self):
        extraction = _make_valid_extraction(acceptance_signal='agreed')
        extraction['pricing']['unit_price'] = None
        result = self.validator.adjust_confidence(extraction)
        self.assertEqual(result['confidence'], 'low')

    def test_high_no_dates_downgrades_to_medium(self):
        extraction = _make_valid_extraction(
            confidence='high',
            acceptance_signal='agreed',
        )
        extraction['license_terms']['start_date'] = ''
        extraction['license_terms']['end_date'] = ''
        result = self.validator.adjust_confidence(extraction)
        self.assertEqual(result['confidence'], 'medium')


# ---------------------------------------------------------------------------
# Thread ingestion tests
# ---------------------------------------------------------------------------

class ThreadIngestionTests(TestCase):
    def test_ingest_happy_path(self):
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        self.assertEqual(thread.conversation_id, 'thread_001')
        self.assertEqual(thread.messages.count(), 7)
        self.assertIn('Bloomberg', thread.subject)
        self.assertTrue(len(thread.flattened_thread) > 0)

    def test_ingest_multi_round(self):
        data = _load_thread_json('thread_002_multi_round.json')
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        self.assertEqual(thread.conversation_id, 'thread_002')
        self.assertEqual(thread.messages.count(), 13)

    def test_ingest_ambiguous(self):
        data = _load_thread_json('thread_003_ambiguous_close.json')
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        self.assertEqual(thread.conversation_id, 'thread_003')
        self.assertEqual(thread.messages.count(), 9)

    def test_flattened_thread_contains_all_messages(self):
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        for i in range(1, 8):
            self.assertIn(f'Message {i} of 7', thread.flattened_thread)

    def test_flattened_thread_contains_participant_roles(self):
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        self.assertIn('(Client)', thread.flattened_thread)
        self.assertIn('(Vendor)', thread.flattened_thread)
        self.assertIn('(Concertiv)', thread.flattened_thread)


# ---------------------------------------------------------------------------
# ClaudeExtractionClient tests (mocked)
# ---------------------------------------------------------------------------

class ClaudeExtractionClientTests(TestCase):
    @patch('extraction.claude_client.Anthropic')
    def test_extract_success(self, MockAnthropic):
        extraction_data = _make_valid_extraction()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(extraction_data))]
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = mock_response

        client = ClaudeExtractionClient(api_key='test-key')
        result = client.extract('test thread text')

        self.assertEqual(result['pricing']['unit_price'], 20500)
        self.assertEqual(result['parties']['client_name'], 'Acme Capital')
        mock_client.messages.create.assert_called_once()

    @patch('extraction.claude_client.Anthropic')
    def test_extract_api_failure_raises(self, MockAnthropic):
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.side_effect = Exception('API down')

        client = ClaudeExtractionClient(api_key='test-key')
        with self.assertRaises(ExtractionError) as ctx:
            client.extract('test thread text')
        self.assertIn('Claude API call failed', str(ctx.exception))

    @patch('extraction.claude_client.Anthropic')
    def test_extract_invalid_json_raises(self, MockAnthropic):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='not json')]
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = mock_response

        client = ClaudeExtractionClient(api_key='test-key')
        with self.assertRaises(ExtractionError) as ctx:
            client.extract('test thread text')
        self.assertIn('Failed to parse', str(ctx.exception))

    @patch('extraction.claude_client.Anthropic')
    def test_extract_validation_failure_raises(self, MockAnthropic):
        bad_data = {'confidence': 'invalid'}  # Missing required sections
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(bad_data))]
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = mock_response

        client = ClaudeExtractionClient(api_key='test-key')
        with self.assertRaises(ExtractionError) as ctx:
            client.extract('test thread text')
        self.assertIn('validation failed', str(ctx.exception))

    @patch('extraction.claude_client.Anthropic')
    def test_extract_markdown_wrapped_response(self, MockAnthropic):
        extraction_data = _make_valid_extraction()
        wrapped = '```json\n' + json.dumps(extraction_data) + '\n```'
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=wrapped)]
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = mock_response

        client = ClaudeExtractionClient(api_key='test-key')
        result = client.extract('test thread text')
        self.assertEqual(result['pricing']['unit_price'], 20500)
