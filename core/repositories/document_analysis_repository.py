from typing import List, Optional, Protocol, runtime_checkable

from core.domain.entities.document_analysis import DocumentAnalysis


@runtime_checkable
class DocumentAnalysisRepositoryProtocol(Protocol):
    """Protocol for DocumentAnalysis repository operations."""

    def save(self, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Save a document analysis.

        Args:
            analysis: The DocumentAnalysis entity to save

        Returns:
            DocumentAnalysis: The saved entity with updated ID
        """
        ...

    def get_by_id(self, analysis_id: int) -> Optional[DocumentAnalysis]:
        """Retrieve a document analysis by ID.

        Args:
            analysis_id: The analysis ID

        Returns:
            DocumentAnalysis if found, None otherwise
        """
        ...

    def get_by_document_id(self, document_id: int) -> Optional[DocumentAnalysis]:
        """Retrieve the latest analysis for a document.

        Args:
            document_id: The document ID

        Returns:
            DocumentAnalysis if found, None otherwise
        """
        ...

    def list_by_document_id(self, document_id: int) -> List[DocumentAnalysis]:
        """List all analyses for a document.

        Args:
            document_id: The document ID

        Returns:
            List of DocumentAnalysis entities
        """
        ...

    def delete(self, analysis_id: int) -> bool:
        """Delete a document analysis.

        Args:
            analysis_id: The analysis ID

        Returns:
            True if deleted, False if not found
        """
        ...


class DocumentAnalysisRepository:
    """Concrete implementation of DocumentAnalysisRepository using Django ORM."""

    def save(self, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Save a document analysis.

        Args:
            analysis: The DocumentAnalysis entity to save

        Returns:
            DocumentAnalysis: The saved entity with updated ID
        """
        from core.orm.models import DocumentAnalysis as DocumentAnalysisModel
        from core.orm.mappers import DocumentAnalysisMapper

        if analysis.id:
            # Update existing analysis
            try:
                model = DocumentAnalysisModel.objects.get(id=analysis.id)
                # Update model fields
                data = DocumentAnalysisMapper.to_model_data(analysis)
                for key, value in data.items():
                    setattr(model, key, value)
                model.save()
                return DocumentAnalysisMapper.to_entity(model)
            except DocumentAnalysisModel.DoesNotExist:  # type: ignore[attr-defined]
                raise ValueError(f"DocumentAnalysis with id {analysis.id} not found")
        else:
            # Create new analysis
            data = DocumentAnalysisMapper.to_model_data(analysis)
            model = DocumentAnalysisModel.objects.create(**data)
            return DocumentAnalysisMapper.to_entity(model)

    def get_by_id(self, analysis_id: int) -> Optional[DocumentAnalysis]:
        """Retrieve a document analysis by ID.

        Args:
            analysis_id: The analysis ID

        Returns:
            DocumentAnalysis if found, None otherwise
        """
        from core.orm.models import DocumentAnalysis as DocumentAnalysisModel
        from core.orm.mappers import DocumentAnalysisMapper

        try:
            model = DocumentAnalysisModel.objects.get(id=analysis_id)
            return DocumentAnalysisMapper.to_entity(model)
        except DocumentAnalysisModel.DoesNotExist:  # type: ignore[attr-defined]
            return None

    def get_by_document_id(self, document_id: int) -> Optional[DocumentAnalysis]:
        """Retrieve the latest analysis for a document.

        Args:
            document_id: The document ID

        Returns:
            DocumentAnalysis if found, None otherwise
        """
        from core.orm.models import DocumentAnalysis as DocumentAnalysisModel
        from core.orm.mappers import DocumentAnalysisMapper

        try:
            model = DocumentAnalysisModel.objects.filter(
                document_id=document_id
            ).order_by('-analyzed_at').first()

            if model:
                return DocumentAnalysisMapper.to_entity(model)
            return None
        except Exception:
            return None

    def list_by_document_id(self, document_id: int) -> List[DocumentAnalysis]:
        """List all analyses for a document.

        Args:
            document_id: The document ID

        Returns:
            List of DocumentAnalysis entities
        """
        from core.orm.models import DocumentAnalysis as DocumentAnalysisModel
        from core.orm.mappers import DocumentAnalysisMapper

        models = DocumentAnalysisModel.objects.filter(
            document_id=document_id
        ).order_by('-analyzed_at')

        return [DocumentAnalysisMapper.to_entity(model) for model in models]

    def delete(self, analysis_id: int) -> bool:
        """Delete a document analysis.

        Args:
            analysis_id: The analysis ID

        Returns:
            True if deleted, False if not found
        """
        from core.orm.models import DocumentAnalysis as DocumentAnalysisModel

        try:
            model = DocumentAnalysisModel.objects.get(id=analysis_id)
            model.delete()
            return True
        except DocumentAnalysisModel.DoesNotExist:  # type: ignore[attr-defined]
            return False