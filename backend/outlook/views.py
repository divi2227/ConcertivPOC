from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .graph_client import OutlookGraphClient, ThreadNotFoundError, AuthenticationError
from threads.models import EmailThread
from threads.services import ThreadIngestionService
from threads.serializers import EmailThreadDetailSerializer


@api_view(['GET'])
def outlook_vendors(request):
    """Return list of vendors from Outlook service."""
    try:
        client = OutlookGraphClient()
        vendors = client.get_vendors()
        return Response({'vendors': vendors})
    except AuthenticationError as e:
        return Response(
            {'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY
        )


@api_view(['GET'])
def outlook_clients(request):
    """Return list of clients from Outlook service."""
    try:
        client = OutlookGraphClient()
        clients = client.get_clients()
        return Response({'clients': clients})
    except AuthenticationError as e:
        return Response(
            {'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY
        )


@api_view(['POST'])
def outlook_fetch(request):
    """Fetch email thread from Outlook service and ingest it."""
    vendor = request.data.get('vendor')
    client_name = request.data.get('client')

    if not vendor or not client_name:
        return Response(
            {'error': 'Both vendor and client are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        graph_client = OutlookGraphClient()
        thread_data = graph_client.fetch_thread(vendor, client_name)
    except ThreadNotFoundError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except AuthenticationError as e:
        return Response(
            {'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch from Outlook: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # Check if thread already exists (same conversation_id)
    conversation_id = thread_data.get('conversation_id', '')
    existing = EmailThread.objects.filter(conversation_id=conversation_id).first()
    if existing:
        serializer = EmailThreadDetailSerializer(existing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    try:
        service = ThreadIngestionService()
        thread = service.ingest_from_json(thread_data)
        serializer = EmailThreadDetailSerializer(thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': f'Failed to ingest thread: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
