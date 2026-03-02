import uuid
from django.db import models
from extraction.models import ExtractedProposal


class GeneratedProposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    extracted_proposal = models.OneToOneField(ExtractedProposal, on_delete=models.CASCADE, related_name='generated_proposal')
    html_content = models.TextField(blank=True, default='')
    pdf_file = models.FileField(upload_to='proposals/', blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Proposal for {self.extracted_proposal.thread.subject}"
