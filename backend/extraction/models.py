import uuid
from django.db import models
from threads.models import EmailThread


class ExtractedProposal(models.Model):
    CONFIDENCE_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.OneToOneField(EmailThread, on_delete=models.CASCADE, related_name='extracted_proposal')
    raw_extraction = models.JSONField(default=dict)
    parties = models.JSONField(default=dict)
    product = models.JSONField(default=dict)
    pricing = models.JSONField(default=dict)
    license_terms = models.JSONField(default=dict)
    sla_terms = models.JSONField(default=dict)
    special_conditions = models.JSONField(default=list)
    ambiguities = models.JSONField(default=list)
    confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES, default='low')
    acceptance_signal = models.TextField(blank=True, default='')
    extraction_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    extracted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Extraction for {self.thread.subject} ({self.confidence})"
