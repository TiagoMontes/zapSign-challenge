from rest_framework import serializers
from typing import List

from core.domain.entities.document_analysis import DocumentAnalysis


class DocumentAnalysisSerializer(serializers.Serializer):
    """Serializer for DocumentAnalysis entities."""

    id = serializers.IntegerField(read_only=True)
    document_id = serializers.IntegerField(read_only=True)
    missing_topics = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="List of potentially missing topics or information"
    )
    summary = serializers.CharField(
        read_only=True,
        help_text="Summary of the document analysis"
    )
    insights = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="Key insights and recommendations from the analysis"
    )
    analyzed_at = serializers.DateTimeField(
        read_only=True,
        help_text="Timestamp when the analysis was performed"
    )

    class Meta:
        help_text = "Document analysis results with AI-generated insights"


class AnalyzeDocumentRequestSerializer(serializers.Serializer):
    """Serializer for document analysis request."""

    force_reanalysis = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Force re-analysis even if analysis already exists"
    )

    class Meta:
        help_text = "Request to analyze a document"


class AnalyzeDocumentResponseSerializer(serializers.Serializer):
    """Serializer for document analysis response."""

    success = serializers.BooleanField(
        help_text="Whether the analysis was successful"
    )
    message = serializers.CharField(
        help_text="Status message"
    )
    analysis = DocumentAnalysisSerializer(
        allow_null=True,
        help_text="The analysis results if successful"
    )

    class Meta:
        help_text = "Response from document analysis operation"