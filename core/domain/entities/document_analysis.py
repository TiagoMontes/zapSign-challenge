from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class DocumentAnalysis:
    """Domain entity representing the analysis of a document."""

    id: Optional[int] = None
    document_id: int = 0
    missing_topics: List[str] = field(default_factory=list)
    summary: str = ""
    insights: List[str] = field(default_factory=list)
    analyzed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize default values and validate entity."""
        if self.missing_topics is None:
            self.missing_topics = []
        if self.insights is None:
            self.insights = []

        if not self.document_id:
            raise ValueError("DocumentAnalysis.document_id is required")

    def add_missing_topic(self, topic: str) -> None:
        """Add a missing topic to the analysis."""
        if topic and topic.strip() and topic not in self.missing_topics:
            self.missing_topics.append(topic.strip())

    def add_insight(self, insight: str) -> None:
        """Add an insight to the analysis."""
        if insight and insight.strip() and insight not in self.insights:
            self.insights.append(insight.strip())

    def has_meaningful_analysis(self) -> bool:
        """Check if the analysis contains meaningful content."""
        return bool(
            self.summary.strip() or
            self.missing_topics or
            self.insights
        )

    def is_complete(self) -> bool:
        """Check if the analysis is complete with all required fields."""
        return (
            bool(self.summary.strip()) and
            self.analyzed_at is not None and
            self.document_id > 0
        )