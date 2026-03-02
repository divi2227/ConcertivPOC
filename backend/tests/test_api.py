import json
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from threads.models import EmailThread, EmailMessage
from threads.services import ThreadIngestionService
from extraction.models import ExtractedProposal

from .test_extraction import _load_thread_json, _make_valid_extraction


class ThreadUploadAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_upload_json_body(self):
        data = _load_thread_json('thread_001_happy_path.json')
        response = self.client.post('/api/threads/upload/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['conversation_id'], 'thread_001')
        self.assertEqual(len(response.data['messages']), 7)

    def test_upload_invalid_json(self):
        response = self.client.post(
            '/api/threads/upload/',
            'not json',
            content_type='application/json',
        )
        self.assertIn(response.status_code, [400, 500])

    def test_upload_duplicate_conversation_id(self):
        data = _load_thread_json('thread_001_happy_path.json')
        self.client.post('/api/threads/upload/', data, format='json')
        response = self.client.post('/api/threads/upload/', data, format='json')
        self.assertEqual(response.status_code, 500)


class ThreadListAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        self.thread = service.ingest_from_json(data)

    def test_list_threads(self):
        response = self.client.get('/api/threads/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['conversation_id'], 'thread_001')

    def test_list_threads_has_extraction_field(self):
        response = self.client.get('/api/threads/')
        self.assertIn('has_extraction', response.data[0])
        self.assertFalse(response.data[0]['has_extraction'])


class ThreadDetailAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        self.thread = service.ingest_from_json(data)

    def test_get_thread_detail(self):
        response = self.client.get(f'/api/threads/{self.thread.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['conversation_id'], 'thread_001')
        self.assertEqual(len(response.data['messages']), 7)
        self.assertIn('flattened_thread', response.data)

    def test_get_nonexistent_thread(self):
        import uuid
        response = self.client.get(f'/api/threads/{uuid.uuid4()}/')
        self.assertEqual(response.status_code, 404)


class AnalyzeThreadAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        self.thread = service.ingest_from_json(data)

    @patch('threads.views.ClaudeExtractionClient')
    def test_analyze_creates_proposal(self, MockClient):
        extraction = _make_valid_extraction()
        mock_instance = MockClient.return_value
        mock_instance.extract.return_value = extraction

        response = self.client.post(f'/api/threads/{self.thread.id}/analyze/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'completed')
        self.assertIn('proposal_id', response.data)
        self.assertTrue(ExtractedProposal.objects.filter(thread=self.thread).exists())

    @patch('threads.views.ClaudeExtractionClient')
    def test_analyze_returns_extraction_data(self, MockClient):
        extraction = _make_valid_extraction()
        mock_instance = MockClient.return_value
        mock_instance.extract.return_value = extraction

        response = self.client.post(f'/api/threads/{self.thread.id}/analyze/')
        self.assertEqual(response.data['extraction']['confidence'], 'high')
        self.assertEqual(response.data['extraction']['pricing']['unit_price'], 20500)

    @patch('threads.views.ClaudeExtractionClient')
    def test_analyze_extraction_error(self, MockClient):
        from extraction.claude_client import ExtractionError
        mock_instance = MockClient.return_value
        mock_instance.extract.side_effect = ExtractionError('API failure')

        response = self.client.post(f'/api/threads/{self.thread.id}/analyze/')
        self.assertEqual(response.status_code, 502)

    def test_analyze_nonexistent_thread(self):
        import uuid
        response = self.client.post(f'/api/threads/{uuid.uuid4()}/analyze/')
        self.assertEqual(response.status_code, 404)


class ProposalDetailAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        extraction = _make_valid_extraction()
        self.proposal = ExtractedProposal.objects.create(
            thread=thread,
            raw_extraction=extraction,
            parties=extraction['parties'],
            product=extraction['product'],
            pricing=extraction['pricing'],
            license_terms=extraction['license_terms'],
            sla_terms=extraction.get('sla_terms', {}),
            special_conditions=[],
            ambiguities=[],
            confidence='high',
            acceptance_signal='agreed',
            extraction_status='completed',
            extracted_at=timezone.now(),
        )

    def test_get_proposal(self):
        response = self.client.get(f'/api/proposals/{self.proposal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['confidence'], 'high')
        self.assertEqual(response.data['pricing']['unit_price'], 20500)

    def test_patch_proposal_confidence(self):
        response = self.client.patch(
            f'/api/proposals/{self.proposal.id}/',
            {'confidence': 'medium'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.confidence, 'medium')

    def test_get_nonexistent_proposal(self):
        import uuid
        response = self.client.get(f'/api/proposals/{uuid.uuid4()}/')
        self.assertEqual(response.status_code, 404)


class GenerateProposalAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        data = _load_thread_json('thread_001_happy_path.json')
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        extraction = _make_valid_extraction()
        self.proposal = ExtractedProposal.objects.create(
            thread=thread,
            raw_extraction=extraction,
            parties=extraction['parties'],
            product=extraction['product'],
            pricing=extraction['pricing'],
            license_terms=extraction['license_terms'],
            sla_terms=extraction.get('sla_terms', {}),
            special_conditions=[],
            ambiguities=[],
            confidence='high',
            acceptance_signal='agreed',
            extraction_status='completed',
            extracted_at=timezone.now(),
        )

    @patch('proposals.generator.ProposalGenerator.generate_pdf', return_value=b'%PDF-fake')
    @patch('proposals.generator.ProposalGenerator._load_css', return_value='')
    def test_generate_proposal(self, mock_css, mock_pdf):
        response = self.client.post(f'/api/proposals/{self.proposal.id}/generate/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('generated_id', response.data)
        self.assertIn('html_content', response.data)
        self.assertIn('Bloomberg', response.data['html_content'])

    def test_generate_nonexistent_proposal(self):
        import uuid
        response = self.client.post(f'/api/proposals/{uuid.uuid4()}/generate/')
        self.assertEqual(response.status_code, 404)
