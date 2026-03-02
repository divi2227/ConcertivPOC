from rest_framework import serializers
from .models import GeneratedProposal


class GeneratedProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedProposal
        fields = ['id', 'html_content', 'generated_at', 'is_approved']
