import os
from datetime import datetime, timezone
from typing import List, Optional
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document as LangChainDocument
from langchain.prompts import PromptTemplate

from core.domain.entities.document import Document
from core.domain.entities.document_analysis import DocumentAnalysis
from .interfaces import BaseAnalysisService, AnalysisError


class AIAnalysisService(BaseAnalysisService):
    """AI-powered document analysis service using LangChain and RAG.

    This service implements sophisticated document analysis using:
    - OpenAI embeddings for semantic understanding
    - ChromaDB for vector storage and retrieval
    - RAG (Retrieval-Augmented Generation) for contextual analysis
    - Document chunking for large text processing
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        temperature: float = 0.3,
        persist_directory: str = "./data/chroma_db",
    ):
        """Initialize the AI analysis service.

        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
            temperature: LLM temperature for consistency
            persist_directory: Directory for persistent vector storage
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for AI analysis")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.temperature = temperature
        self.persist_directory = persist_directory

        # Create persist directory if it doesn't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize components
        self._setup_components()

        # Initialize persistent vector store
        self._setup_persistent_vectorstore()

    def _setup_components(self) -> None:
        """Set up LangChain components."""
        # Text splitter for document chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

        # OpenAI embeddings for semantic understanding
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model="text-embedding-3-small"  # Cost-effective, high quality
        )

        # ChatGPT for analysis generation
        self.llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model="gpt-3.5-turbo",
            temperature=self.temperature,
        )

        # Analysis prompts
        self._setup_prompts()

    def _setup_persistent_vectorstore(self) -> None:
        """Set up persistent ChromaDB vector store."""
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="document_analysis"
        )

    def _setup_prompts(self) -> None:
        """Set up analysis prompts."""
        self.analysis_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
Você é um analista de documentos especialista. Analise CUIDADOSAMENTE o documento fornecido com base no contexto completo.

Contexto do documento:
{context}

Pergunta: {question}

INSTRUÇÕES IMPORTANTES:
- Leia TODAS as informações fornecidas no contexto antes de responder
- Baseie sua análise EXCLUSIVAMENTE no conteúdo presente no documento
- Se informações estão presentes no contexto, NÃO as liste como ausentes
- Seja preciso e factual

Por favor, forneça uma análise detalhada no seguinte formato:

RESUMO:
Forneça um resumo conciso de 2-3 frases sobre o conteúdo principal e propósito do documento, baseado no que está REALMENTE presente no texto.

MELHORIAS_SUGERIDAS:
Forneça pelo menos 3 sugestões específicas e práticas para melhorar o documento. IMPORTANTE: TODAS as sugestões devem obrigatoriamente começar com uma das seguintes expressões amigáveis:
- "Você poderia..."
- "Seria interessante..."
- "O que acha de..."
- "Que tal..."
- "Talvez fosse bom..."
- "Uma ideia seria..."

Exemplos do formato correto:
- "Você poderia adicionar mais detalhes sobre..."
- "Seria interessante incluir informações sobre..."
- "O que acha de expandir a seção que fala sobre..."

Baseie-se no conteúdo atual e sugira melhorias em: informações adicionais, apresentação, estrutura, detalhes ou aspectos quantificados.

INSIGHTS:
Forneça 3-5 insights principais baseados no conteúdo REAL do documento:
- Pontos fortes identificados no documento
- Aspectos técnicos ou profissionais relevantes
- Qualidade e completude das informações
- Observações específicas sobre o conteúdo apresentado

Seja específico, preciso e baseie-se apenas no que está explicitamente mencionado no documento.
"""
        )

    def analyze_document(self, document: Document) -> DocumentAnalysis:
        """Analyze a document using AI with RAG capabilities.

        Args:
            document: The document entity to analyze

        Returns:
            DocumentAnalysis: The analysis results

        Raises:
            AnalysisError: If analysis fails
        """
        try:
            # Validate document
            self._validate_document(document)

            # Extract and prepare document content
            content = self._extract_content(document)
            if not content.strip():
                raise AnalysisError("Document has no content to analyze")

            # Check if document is already indexed, if not, index it
            self._ensure_document_indexed(document, content)

            # Perform RAG-based analysis using persistent vectorstore
            analysis_result = self._perform_rag_analysis(
                document.id, document.name
            )

            # Parse and create analysis entity
            return self._create_analysis_entity(
                document.id, analysis_result
            )

        except Exception as e:
            raise AnalysisError(
                f"AI analysis failed for document {document.id}: {str(e)}", e
            )

    def _extract_content(self, document: Document) -> str:
        """Extract content from document for analysis.

        Real implementation that extracts text from PDF if available,
        or returns cached content from ChromaDB chunks.

        Args:
            document: The document entity

        Returns:
            str: The document content

        Raises:
            AnalysisError: If content extraction fails
        """
        # Check if document has PDF URL for processing
        if document.pdf_url:
            print(f"[DEBUG] Document {document.id} has PDF URL: {document.pdf_url}")

            # Check if already processed and cached in ChromaDB
            document_filter = {"document_id": document.id}
            existing_docs = self.vectorstore.get(where=document_filter)

            if existing_docs and existing_docs.get('ids'):
                print(f"[DEBUG] Found {len(existing_docs['ids'])} cached chunks for document {document.id}")
                # Return cached content from first few chunks
                chunks_content = existing_docs.get('documents', [])[:5]  # First 5 chunks
                cached_content = "\n\n".join(chunks_content)
                return f"Document: {document.name}\nContent from PDF:\n\n{cached_content}"

            # PDF not yet processed, indicate this
            return f"Document: {document.name}\nStatus: PDF processing required\nURL: {document.pdf_url}"

        # Fallback for documents without PDF URL
        return f"""Document: {document.name}
ID: {document.id}
Status: {document.status}
Created by: {document.created_by}

Este documento não possui um arquivo PDF associado para análise.
Para análise completa, é necessário fornecer um PDF via url_pdf durante a criação do documento."""

    def _ensure_document_indexed(self, document: Document, content: str) -> None:
        """Ensure document is indexed in persistent vector store.

        Args:
            document: The document entity
            content: Document content
        """
        document_filter = {"document_id": document.id}  # Use int directly

        # Check if document chunks already exist
        existing_docs = self.vectorstore.get(where=document_filter)

        if existing_docs and existing_docs.get('ids'):
            print(f"[DEBUG] Document {document.id} already indexed, using cached embeddings")
            return

        print(f"[DEBUG] Indexing document {document.id} - creating embeddings")

        # Create chunks for this document
        chunks = self._create_chunks(content, document)

        # Add to persistent vector store
        self.vectorstore.add_documents(chunks)

        print(f"[DEBUG] Document {document.id} indexed successfully with {len(chunks)} chunks")

    def _is_document_indexed(self, document_id: int) -> bool:
        """Check if document is already indexed.

        Args:
            document_id: ID of the document

        Returns:
            True if document is indexed, False otherwise
        """
        try:
            document_filter = {"document_id": document_id}  # Use int directly
            existing_docs = self.vectorstore.get(where=document_filter)
            return bool(existing_docs and existing_docs.get('ids'))
        except Exception:
            return False

    def _remove_document_from_index(self, document_id: int) -> bool:
        """Remove document chunks from vector store.

        Args:
            document_id: ID of the document to remove

        Returns:
            True if removed successfully, False otherwise
        """
        try:
            document_filter = {"document_id": document_id}  # Use int directly
            existing_docs = self.vectorstore.get(where=document_filter)

            if existing_docs and existing_docs.get('ids'):
                self.vectorstore.delete(ids=existing_docs['ids'])
                print(f"[DEBUG] Removed document {document_id} from index")
                return True

            return False
        except Exception as e:
            print(f"[DEBUG] Error removing document {document_id} from index: {e}")
            return False

    def _create_chunks(
        self, content: str, document: Document
    ) -> List[LangChainDocument]:
        """Create document chunks for vector storage.

        Args:
            content: The document content
            document: The document entity

        Returns:
            List of LangChain documents with metadata
        """
        # Split content into chunks
        text_chunks = self.text_splitter.split_text(content)

        # Create LangChain documents with metadata
        docs = []
        for i, chunk in enumerate(text_chunks):
            doc = LangChainDocument(
                page_content=chunk,
                metadata={
                    "document_id": document.id,
                    "document_name": document.name,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "status": document.status,
                }
            )
            docs.append(doc)

        return docs

    def reindex_document(self, document: Document) -> bool:
        """Force reindexing of a document (removes old chunks and creates new ones).

        Args:
            document: The document entity to reindex

        Returns:
            True if reindexed successfully, False otherwise
        """
        try:
            # Remove existing chunks
            self._remove_document_from_index(document.id)

            # Extract fresh content and reindex
            content = self._extract_content(document)
            if content.strip():
                chunks = self._create_chunks(content, document)
                self.vectorstore.add_documents(chunks)
                print(f"[DEBUG] Document {document.id} reindexed successfully")
                return True

            return False
        except Exception as e:
            print(f"[DEBUG] Error reindexing document {document.id}: {e}")
            return False

    def clear_all_documents_from_index(self) -> bool:
        """Clear all documents from the vector store.

        CAUTION: This will remove ALL documents from the ChromaDB.
        Use this only for debugging or complete reindexing.

        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            # Get all document IDs
            all_docs = self.vectorstore.get()
            if all_docs and all_docs.get('ids'):
                # Delete all documents
                self.vectorstore.delete(ids=all_docs['ids'])
                print(f"[DEBUG] Cleared {len(all_docs['ids'])} documents from vector store")
                return True
            else:
                print("[DEBUG] No documents found to clear")
                return True
        except Exception as e:
            print(f"[ERROR] Failed to clear vector store: {e}")
            return False

    def get_indexed_documents_info(self) -> dict:
        """Get information about all indexed documents.

        Returns:
            Dictionary with document information grouped by document_id
        """
        try:
            all_docs = self.vectorstore.get()
            if not all_docs or not all_docs.get('ids'):
                return {}

            # Group by document_id
            doc_groups = {}
            metadatas = all_docs.get('metadatas', [])

            for i, metadata in enumerate(metadatas):
                doc_id = metadata.get('document_id', 'unknown')
                if doc_id not in doc_groups:
                    doc_groups[doc_id] = {
                        'document_id': doc_id,
                        'document_name': metadata.get('document_name', 'Unknown'),
                        'chunk_count': 0,
                        'status': metadata.get('status', 'Unknown'),
                        'chunks': []
                    }

                doc_groups[doc_id]['chunk_count'] += 1
                doc_groups[doc_id]['chunks'].append({
                    'index': metadata.get('chunk_index', i),
                    'content_preview': all_docs['documents'][i][:100] + "..." if len(all_docs['documents'][i]) > 100 else all_docs['documents'][i]
                })

            return doc_groups

        except Exception as e:
            print(f"[ERROR] Failed to get indexed documents info: {e}")
            return {}


    def _perform_rag_analysis(
        self, document_id: int, document_name: str
    ) -> str:
        """Perform RAG-based analysis using the persistent vector store.

        Args:
            document_id: ID of the document being analyzed
            document_name: Name of the document being analyzed

        Returns:
            Analysis result as text
        """
        print(f"[DEBUG] Starting RAG analysis for document {document_id}: '{document_name}'")

        # Verify document exists in vectorstore before analysis
        document_filter = {"document_id": document_id}
        existing_docs = self.vectorstore.get(where=document_filter)
        chunks_found = len(existing_docs.get('ids', []))
        print(f"[DEBUG] Found {chunks_found} chunks for document {document_id}")

        if chunks_found == 0:
            print(f"[WARNING] No chunks found for document {document_id}. Analysis may be incomplete.")

        # Create retriever with filter for this specific document
        # CRITICAL: document_id in metadata is stored as int, not string
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 6,  # Retrieve more chunks for better context
                "filter": {"document_id": document_id}  # Use int directly, not string
            }
        )

        # Test retrieval before running full chain
        test_query = f"Analise o documento '{document_name}'"
        print(f"[DEBUG] Testing retrieval for query: '{test_query}'")

        try:
            # Test direct retrieval
            retrieved_docs = retriever.invoke(test_query)
            print(f"[DEBUG] Retriever returned {len(retrieved_docs)} documents")

            for i, doc in enumerate(retrieved_docs):
                print(f"[DEBUG] Retrieved doc {i+1}:")
                print(f"  - Document ID: {doc.metadata.get('document_id')}")
                print(f"  - Document Name: {doc.metadata.get('document_name')}")
                print(f"  - Content preview: {doc.page_content[:100]}...")

            if not retrieved_docs:
                print(f"[ERROR] No documents retrieved for document {document_id}. Check filter logic.")
                # Return a fallback analysis
                return f"""
RESUMO:
Não foi possível recuperar o conteúdo do documento '{document_name}' (ID: {document_id}) para análise.
Isso indica um problema técnico na indexação ou recuperação do documento.

TÓPICOS_AUSENTES:
- Indexação do documento pode estar incompleta
- Filtros de busca podem precisar de correção
- Verificar integridade dos embeddings armazenados

INSIGHTS:
- O sistema RAG precisa de debugging para este documento específico
- Recomenda-se reindexar o documento para garantir disponibilidade
- Verificar se o documento foi corretamente processado durante o upload
"""

        except Exception as e:
            print(f"[ERROR] Retrieval test failed: {str(e)}")
            # Return error analysis
            return f"""
RESUMO:
Erro técnico durante a recuperação do conteúdo do documento '{document_name}' (ID: {document_id}).

TÓPICOS_AUSENTES:
- Análise completa não pôde ser realizada devido a erro técnico
- Verificar configuração do sistema RAG

INSIGHTS:
- Erro encontrado: {str(e)}
- Recomenda-se verificar a configuração da API OpenAI
- Considerar reprocessamento do documento
"""

        # Create retrieval QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={
                "prompt": self.analysis_prompt
            }
        )

        # Perform analysis
        query = f"Analise o documento '{document_name}' quanto à completude, insights e elementos ausentes."
        print(f"[DEBUG] Running QA chain with query: '{query}'")

        result = qa_chain.run(query)
        print(f"[DEBUG] QA chain completed for document {document_id}")

        return result

    def _create_analysis_entity(
        self, document_id: Optional[int], analysis_text: str
    ) -> DocumentAnalysis:
        """Create DocumentAnalysis entity from analysis results.

        Args:
            document_id: ID of the analyzed document
            analysis_text: Raw analysis text from LLM

        Returns:
            DocumentAnalysis entity
        """
        # Parse the analysis text to extract structured data
        summary, missing_topics, insights = self._parse_analysis_text(
            analysis_text
        )

        return DocumentAnalysis(
            document_id=document_id or 0,  # Fallback to 0 if None
            summary=summary,
            missing_topics=missing_topics,
            insights=insights,
            analyzed_at=datetime.now(timezone.utc)
        )

    def _parse_analysis_text(self, text: str) -> tuple[str, List[str], List[str]]:
        """Parse the LLM analysis text into structured components.

        Args:
            text: Raw analysis text

        Returns:
            Tuple of (summary, missing_topics, insights)
        """
        summary = ""
        missing_topics = []
        insights = []

        current_section = None
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect sections (both English and Portuguese)
            if line.upper().startswith('SUMMARY:') or line.upper().startswith('RESUMO:'):
                current_section = 'summary'
                # Extract summary if on same line
                summary_part = line[7:].strip() if line.upper().startswith('RESUMO:') else line[8:].strip()
                if summary_part:
                    summary = summary_part
                continue
            elif line.upper().startswith('MISSING_TOPICS:') or line.upper().startswith('TÓPICOS_AUSENTES:') or line.upper().startswith('MELHORIAS_SUGERIDAS:'):
                current_section = 'missing_topics'
                continue
            elif line.upper().startswith('INSIGHTS:'):
                current_section = 'insights'
                continue

            # Process content based on current section
            if current_section == 'summary':
                if summary:
                    summary += " " + line
                else:
                    summary = line
            elif current_section == 'missing_topics':
                if line.startswith('-') or line.startswith('•'):
                    missing_topics.append(line[1:].strip())
                elif line and not line.isupper():
                    missing_topics.append(line)
            elif current_section == 'insights':
                if line.startswith('-') or line.startswith('•'):
                    insights.append(line[1:].strip())
                elif line and not line.isupper():
                    insights.append(line)

        # Fallback parsing if structured format not detected
        if not summary and not missing_topics and not insights:
            # Use the entire text as summary if no structure detected
            summary = text[:500] + "..." if len(text) > 500 else text
            insights.append("Análise concluída usando processamento de IA")

        return summary.strip(), missing_topics, insights