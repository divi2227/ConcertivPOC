from rest_framework import serializers
from .models import ExtractedProposal


class ExtractedProposalSerializer(serializers.ModelSerializer):
    thread_id = serializers.UUIDField(source='thread.id', read_only=True)
    thread_subject = serializers.CharField(source='thread.subject', read_only=True)

    class Meta:
        model = ExtractedProposal
        fields = [
            'id', 'thread_id', 'thread_subject',
            'parties', 'product', 'pricing', 'license_terms',
            'sla_terms', 'special_conditions', 'ambiguities',
            'confidence', 'acceptance_signal',
            'extraction_status', 'extracted_at',
        ]

    def update(self, instance, validated_data):
        """Allow partial updates to extracted fields."""
        for field in ['parties', 'product', 'pricing', 'license_terms',
                      'sla_terms', 'special_conditions', 'ambiguities',
                      'confidence', 'acceptance_signal']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
