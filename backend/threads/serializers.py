from rest_framework import serializers
from .models import EmailThread, EmailMessage


class EmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailMessage
        fields = ['id', 'message_id', 'sender_name', 'sender_email', 'recipients', 'timestamp', 'raw_body', 'clean_body']


class EmailThreadListSerializer(serializers.ModelSerializer):
    has_extraction = serializers.SerializerMethodField()

    class Meta:
        model = EmailThread
        fields = ['id', 'conversation_id', 'subject', 'participants', 'created_at', 'has_extraction']

    def get_has_extraction(self, obj):
        return hasattr(obj, 'extracted_proposal')


class EmailThreadDetailSerializer(serializers.ModelSerializer):
    messages = EmailMessageSerializer(many=True, read_only=True)

    class Meta:
        model = EmailThread
        fields = ['id', 'conversation_id', 'subject', 'participants', 'flattened_thread', 'created_at', 'messages']
