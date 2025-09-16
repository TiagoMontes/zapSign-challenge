import re
from datetime import datetime, timezone
from typing import List, Set

from core.domain.entities.document import Document
from core.domain.entities.document_analysis import DocumentAnalysis
from .interfaces import BaseAnalysisService


class HeuristicAnalysisService(BaseAnalysisService):
    """Simple heuristic-based document analysis service.

    This service provides basic document analysis without external dependencies,
    serving as a fallback when AI services are unavailable or for development/testing.
    """

    def __init__(self):
        """Initialize the heuristic analysis service."""
        # Define keywords for different document types
        self.contract_keywords = {
            'payment', 'terms', 'conditions', 'obligations', 'liability',
            'termination', 'breach', 'delivery', 'warranty', 'indemnity'
        }

        self.proposal_keywords = {
            'scope', 'timeline', 'budget', 'deliverables', 'milestones',
            'requirements', 'specifications', 'objectives', 'proposal'
        }

        self.legal_keywords = {
            'agreement', 'party', 'parties', 'whereas', 'therefore',
            'shall', 'will', 'clause', 'section', 'article'
        }

        # Common missing elements for different document types
        self.common_missing_elements = {
            'contract': [
                'Payment terms and conditions',
                'Termination clauses',
                'Liability limitations',
                'Dispute resolution procedures',
                'Force majeure provisions'
            ],
            'proposal': [
                'Detailed timeline',
                'Cost breakdown',
                'Risk assessment',
                'Success metrics',
                'Acceptance criteria'
            ],
            'legal': [
                'Governing law',
                'Jurisdiction clauses',
                'Amendment procedures',
                'Notice requirements',
                'Signature blocks'
            ]
        }

    def analyze_document(self, document: Document) -> DocumentAnalysis:
        """Analyze a document using heuristic rules.

        Args:
            document: The document entity to analyze

        Returns:
            DocumentAnalysis: The analysis results
        """
        # Validate document
        self._validate_document(document)

        # Extract document content for analysis
        content = self._extract_content(document)

        # Determine document type
        doc_type = self._classify_document_type(document, content)

        # Generate summary
        summary = self._generate_summary(document, doc_type, content)

        # Identify missing topics
        missing_topics = self._identify_missing_topics(doc_type, content)

        # Generate insights
        insights = self._generate_insights(document, doc_type, content)

        return DocumentAnalysis(
            document_id=document.id,
            summary=summary,
            missing_topics=missing_topics,
            insights=insights,
            analyzed_at=datetime.now(timezone.utc)
        )

    def _extract_content(self, document: Document) -> str:
        """Extract content from document for analysis.

        This is a simplified version for heuristic analysis.

        Args:
            document: The document entity

        Returns:
            str: The document content
        """
        # For heuristic analysis, we'll use available metadata
        content_parts = [
            document.name,
            document.status,
            document.created_by,
        ]

        # Add some simulated content based on document name
        content = " ".join(filter(None, content_parts)).lower()

        return content

    def _classify_document_type(self, document: Document, content: str) -> str:
        """Classify document type based on name and content.

        Args:
            document: The document entity
            content: Document content

        Returns:
            str: Document type classification
        """
        content_lower = content.lower()
        name_lower = document.name.lower()

        # Check for contract keywords
        if any(keyword in name_lower or keyword in content_lower
               for keyword in ['contract', 'agreement']):
            return 'contract'

        # Check for proposal keywords
        if any(keyword in name_lower or keyword in content_lower
               for keyword in ['proposal', 'quote', 'bid']):
            return 'proposal'

        # Check for legal document keywords
        if any(keyword in name_lower or keyword in content_lower
               for keyword in ['legal', 'terms', 'policy']):
            return 'legal'

        # Default classification
        return 'general'

    def _generate_summary(self, document: Document, doc_type: str, content: str) -> str:
        """Generate a summary based on document metadata and type.

        Args:
            document: The document entity
            doc_type: Document type classification
            content: Document content

        Returns:
            str: Generated summary
        """
        summaries = {
            'contract': f"Contract document '{document.name}' with status '{document.status}'. "
                       f"Created by {document.created_by}. Contains terms and conditions for legal agreement.",

            'proposal': f"Proposal document '{document.name}' with status '{document.status}'. "
                       f"Prepared by {document.created_by}. Outlines project scope and requirements.",

            'legal': f"Legal document '{document.name}' with status '{document.status}'. "
                    f"Created by {document.created_by}. Contains legal terms and provisions.",

            'general': f"Document '{document.name}' with status '{document.status}'. "
                      f"Created by {document.created_by}. General business document requiring review."
        }

        return summaries.get(doc_type, summaries['general'])

    def _identify_missing_topics(self, doc_type: str, content: str) -> List[str]:
        """Identify potentially missing topics based on document type.

        Args:
            doc_type: Document type classification
            content: Document content

        Returns:
            List of potentially missing topics
        """
        if doc_type not in self.common_missing_elements:
            return ["Review for completeness", "Verify all required sections"]

        # Get common missing elements for this document type
        potential_missing = self.common_missing_elements[doc_type].copy()

        # For heuristic analysis, randomly select some as potentially missing
        # In a real implementation, this would check for actual presence
        content_lower = content.lower()

        # Simple keyword-based filtering
        missing = []
        for element in potential_missing:
            # Check if element keywords are present in content
            element_keywords = element.lower().split()
            if not any(keyword in content_lower for keyword in element_keywords):
                missing.append(element)

        # Limit to 3-5 items for practical review
        return missing[:5]

    def _generate_insights(self, document: Document, doc_type: str, content: str) -> List[str]:
        """Generate insights based on document analysis.

        Args:
            document: The document entity
            doc_type: Document type classification
            content: Document content

        Returns:
            List of insights
        """
        insights = []

        # Status-based insights
        if document.status in ['', 'draft']:
            insights.append("Document is in draft status and may require final review before execution")

        if document.status == 'pending':
            insights.append("Document is pending and may need stakeholder approval")

        # Type-specific insights
        if doc_type == 'contract':
            insights.extend([
                "Ensure all parties have reviewed and agreed to terms",
                "Verify compliance with organizational policies",
                "Consider legal review for risk mitigation"
            ])
        elif doc_type == 'proposal':
            insights.extend([
                "Review timeline and resource allocation carefully",
                "Ensure all requirements are clearly specified",
                "Consider competitive positioning and pricing"
            ])
        elif doc_type == 'legal':
            insights.extend([
                "Legal documentation requires expert review",
                "Ensure compliance with applicable regulations",
                "Verify all legal requirements are met"
            ])

        # General insights
        insights.extend([
            "Document analysis completed using heuristic methods",
            "Consider AI-powered analysis for more detailed insights"
        ])

        # Return up to 5 insights
        return insights[:5]