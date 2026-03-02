from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ExtractedProposal
from .serializers import ExtractedProposalSerializer


@api_view(['GET', 'PATCH'])
def proposal_detail(request, pk):
    """Get or update an extracted proposal."""
    try:
        proposal = ExtractedProposal.objects.get(pk=pk)
    except ExtractedProposal.DoesNotExist:
        return Response({'error': 'Proposal not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExtractedProposalSerializer(proposal)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = ExtractedProposalSerializer(proposal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
