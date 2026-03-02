import uuid
from django.db import models


class EmailThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_id = models.CharField(max_length=255, unique=True)
    subject = models.TextField()
    participants = models.JSONField(default=list)  # [{name, email, role}]
    raw_messages = models.JSONField(default=list)
    flattened_thread = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.conversation_id}: {self.subject}"


class EmailMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(EmailThread, on_delete=models.CASCADE, related_name='messages')
    message_id = models.CharField(max_length=255)
    sender_name = models.CharField(max_length=255)
    sender_email = models.EmailField()
    recipients = models.JSONField(default=list)
    timestamp = models.DateTimeField()
    raw_body = models.TextField()
    clean_body = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.message_id}: {self.sender_name}"
