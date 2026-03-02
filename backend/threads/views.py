import json
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from django.utils import timezone

from .models import EmailThread
from .serializers import EmailThreadListSerializer, EmailThreadDetailSerializer
from .services import ThreadIngestionService
from extraction.claude_client import ClaudeExtractionClient, ExtractionError
from extraction.models import ExtractedProposal


@api_view(['POST'])
@parser_classes([MultiPartParser, JSONParser])
def upload_thread(request):
    """Upload a JSON thread file or raw JSON body."""
    try:
        if 'file' in request.FILES:
            file = request.FILES['file']
            data = json.loads(file.read().decode('utf-8'))
        else:
            data = request.data
        service = ThreadIngestionService()
        thread = service.ingest_from_json(data)
        serializer = EmailThreadDetailSerializer(thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except (json.JSONDecodeError, KeyError) as e:
        return Response({'error': f'Invalid JSON: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_threads(request):
    """List all email threads."""
    threads = EmailThread.objects.all().order_by('-created_at')
    serializer = EmailThreadListSerializer(threads, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def thread_detail(request, pk):
    """Get thread detail with messages."""
    try:
        thread = EmailThread.objects.get(pk=pk)
    except EmailThread.DoesNotExist:
        return Response({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = EmailThreadDetailSerializer(thread)
    return Response(serializer.data)


@api_view(['POST'])
def analyze_thread(request, pk):
    """Trigger Claude extraction on a thread."""
    try:
        thread = EmailThread.objects.get(pk=pk)
    except EmailThread.DoesNotExist:
        return Response({'error': 'Thread not found'}, status=status.HTTP_404_NOT_FOUND)

    if not thread.flattened_thread:
        return Response({'error': 'Thread has no flattened content'}, status=status.HTTP_400_BAD_REQUEST)

    client = ClaudeExtractionClient()
    try:
        result = client.extract(thread.flattened_thread)
    except ExtractionError as e:
        return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    proposal, _ = ExtractedProposal.objects.update_or_create(
        thread=thread,
        defaults={
            'raw_extraction': result,
            'parties': result.get('parties', {}),
            'product': result.get('product', {}),
            'pricing': result.get('pricing', {}),
            'license_terms': result.get('license_terms', {}),
            'sla_terms': result.get('sla_terms', {}),
            'special_conditions': result.get('special_conditions', []),
            'ambiguities': result.get('ambiguities', []),
            'confidence': result.get('confidence', 'low'),
            'acceptance_signal': result.get('acceptance_signal', ''),
            'extraction_status': 'completed',
            'extracted_at': timezone.now(),
        }
    )

    from extraction.serializers import ExtractedProposalSerializer
    serializer = ExtractedProposalSerializer(proposal)
    return Response({'proposal_id': str(proposal.id), 'status': 'completed', 'extraction': serializer.data})
