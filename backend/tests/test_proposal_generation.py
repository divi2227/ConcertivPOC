from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone

from threads.models import EmailThread
from threads.services import ThreadIngestionService
from extraction.models import ExtractedProposal
from proposals.models import GeneratedProposal
from proposals.generator import ProposalGenerator

from .test_extraction import _load_thread_json, _make_valid_extraction


def _create_thread_and_proposal(thread_file='thread_001_happy_path.json', **extraction_overrides):
    """Helper: ingest a thread and create an ExtractedProposal."""
    data = _load_thread_json(thread_file)
    service = ThreadIngestionService()
    thread = service.ingest_from_json(data)

    extraction = _make_valid_extraction(**extraction_overrides)
    proposal = ExtractedProposal.objects.create(
        thread=thread,
        raw_extraction=extraction,
        parties=extraction['parties'],
        product=extraction['product'],
        pricing=extraction['pricing'],
        license_terms=extraction['license_terms'],
        sla_terms=extraction.get('sla_terms', {}),
        special_conditions=extraction.get('special_conditions', []),
        ambiguities=extraction.get('ambiguities', []),
        confidence=extraction['confidence'],
        acceptance_signal=extraction.get('acceptance_signal', ''),
        extraction_status='completed',
        extracted_at=timezone.now(),
    )
    return thread, proposal


class ProposalGeneratorHTMLTests(TestCase):
    def setUp(self):
        self.thread, self.proposal = _create_thread_and_proposal()

    @patch.object(ProposalGenerator, '_load_css', return_value='body { margin: 0; }')
    def test_generate_html_returns_string(self, mock_css):
        gen = ProposalGenerator()
        html = gen.generate_html(self.proposal)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 100)

    @patch.object(ProposalGenerator, '_load_css', return_value='')
    def test_html_contains_parties(self, mock_css):
        gen = ProposalGenerator()
        html = gen.generate_html(self.proposal)
        self.assertIn('Acme Capital', html)
        self.assertIn('Bloomberg LP', html)

    @patch.object(ProposalGenerator, '_load_css', return_value='')
    def test_html_contains_pricing(self, mock_css):
        gen = ProposalGenerator()
        html = gen.generate_html(self.proposal)
        self.assertIn('20,500', html)

    @patch.object(ProposalGenerator, '_load_css', return_value='')
    def test_html_contains_subject(self, mock_css):
        gen = ProposalGenerator()
        html = gen.generate_html(self.proposal)
        # Subject appears in title tag and/or executive summary
        self.assertIn('Bloomberg Terminal', html)

    @patch.object(ProposalGenerator, '_load_css', return_value='')
    def test_html_contains_ref_number(self, mock_css):
        gen = ProposalGenerator()
        html = gen.generate_html(self.proposal)
        self.assertIn('PRO-', html)


class ExecutiveSummaryTests(TestCase):
    def test_high_confidence_summary(self):
        _, proposal = _create_thread_and_proposal(confidence='high', acceptance_signal='agreed')
        gen = ProposalGenerator()
        summary = gen._build_executive_summary(proposal)
        self.assertIn('explicitly confirmed', summary)

    def test_medium_confidence_summary(self):
        _, proposal = _create_thread_and_proposal(
            thread_file='thread_002_multi_round.json',
            confidence='medium',
            acceptance_signal='implied',
        )
        gen = ProposalGenerator()
        summary = gen._build_executive_summary(proposal)
        self.assertIn('implied acceptance', summary)

    def test_low_confidence_summary(self):
        _, proposal = _create_thread_and_proposal(
            thread_file='thread_003_ambiguous_close.json',
            confidence='low',
            acceptance_signal='',
        )
        gen = ProposalGenerator()
        summary = gen._build_executive_summary(proposal)
        self.assertIn('under discussion', summary)

    def test_summary_includes_pricing_details(self):
        _, proposal = _create_thread_and_proposal()
        gen = ProposalGenerator()
        summary = gen._build_executive_summary(proposal)
        self.assertIn('$20,500', summary)
        self.assertIn('18', summary)


class GeneratedProposalModelTests(TestCase):
    def test_create_generated_proposal(self):
        _, extracted = _create_thread_and_proposal()
        gen_proposal = GeneratedProposal.objects.create(
            extracted_proposal=extracted,
            html_content='<html>test</html>',
            generated_at=timezone.now(),
        )
        self.assertEqual(str(gen_proposal), f'Proposal for {extracted.thread.subject}')
        self.assertFalse(gen_proposal.is_approved)
