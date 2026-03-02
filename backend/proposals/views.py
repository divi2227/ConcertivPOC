from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.core.files.base import ContentFile

from extraction.models import ExtractedProposal
from .models import GeneratedProposal
from .generator import ProposalGenerator


@api_view(['POST'])
def generate_proposal(request, pk):
    """Generate HTML and PDF proposal from extraction."""
    try:
        extracted = ExtractedProposal.objects.get(pk=pk)
    except ExtractedProposal.DoesNotExist:
        return Response({'error': 'Extracted proposal not found'}, status=status.HTTP_404_NOT_FOUND)

    gen = ProposalGenerator()
    html = gen.generate_html(extracted)
    pdf_bytes = gen.generate_pdf(html)

    proposal, _ = GeneratedProposal.objects.update_or_create(
        extracted_proposal=extracted,
        defaults={
            'html_content': html,
            'generated_at': timezone.now(),
        }
    )
    proposal.pdf_file.save(
        f"proposal_{extracted.id}.pdf",
        ContentFile(pdf_bytes),
        save=True
    )

    return Response({
        'generated_id': str(proposal.id),
        'html_content': html,
    })


@api_view(['GET'])
def download_proposal(request, pk):
    """Download generated PDF."""
    try:
        extracted = ExtractedProposal.objects.get(pk=pk)
        proposal = extracted.generated_proposal
    except (ExtractedProposal.DoesNotExist, GeneratedProposal.DoesNotExist):
        return Response({'error': 'Proposal not found'}, status=status.HTTP_404_NOT_FOUND)

    if not proposal.pdf_file:
        return Response({'error': 'PDF not generated yet'}, status=status.HTTP_404_NOT_FOUND)

    return FileResponse(proposal.pdf_file.open('rb'), content_type='application/pdf',
                        as_attachment=True, filename=f'proposal_{pk}.pdf')
