import json
from .models import EmailThread, EmailMessage


class ThreadIngestionService:
    def ingest_from_json(self, data: dict) -> EmailThread:
        """Parse JSON thread data and create EmailThread + EmailMessages."""
        thread = EmailThread.objects.create(
            conversation_id=data['conversation_id'],
            subject=data['subject'],
            participants=data.get('participants', []),
            raw_messages=data.get('messages', []),
        )
        for msg_data in data.get('messages', []):
            EmailMessage.objects.create(
                thread=thread,
                message_id=msg_data['message_id'],
                sender_name=msg_data['from']['name'],
                sender_email=msg_data['from']['email'],
                recipients=msg_data.get('to', []) + msg_data.get('cc', []),
                timestamp=msg_data['timestamp'],
                raw_body=msg_data['body'],
                clean_body=msg_data['body'],  # For POC, no quote stripping
            )
        # Flatten thread
        thread.flattened_thread = self.flatten_thread(thread)
        thread.save()
        return thread

    def flatten_thread(self, thread: EmailThread) -> str:
        """Build chronological plain-text representation for Claude."""
        messages = thread.messages.order_by('timestamp')
        total = messages.count()
        lines = []
        for i, msg in enumerate(messages, 1):
            # Find participant role
            role = 'Unknown'
            for p in thread.participants:
                if p.get('email', '').lower() == msg.sender_email.lower():
                    role = p.get('role', 'Unknown').capitalize()
                    break
            lines.append(f"--- Message {i} of {total} [{msg.message_id}] ---")
            lines.append(f"From: {msg.sender_name} <{msg.sender_email}> ({role})")
            recipients_str = ', '.join(
                f"{r.get('name', '')} <{r.get('email', '')}>" for r in msg.recipients
            )
            lines.append(f"To: {recipients_str}")
            lines.append(f"Date: {msg.timestamp.isoformat()}")
            lines.append(f"Subject: {thread.subject}")
            lines.append('')
            lines.append(msg.clean_body)
            lines.append('')
        return '\n'.join(lines)
