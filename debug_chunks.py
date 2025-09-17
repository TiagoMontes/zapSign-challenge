#!/usr/bin/env python3
"""
Script para debugar chunks e embeddings no ChromaDB
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services.analysis.ai_service import AIAnalysisService
from core.repositories.document_repo import DjangoDocumentRepository

def debug_chroma_contents():
    """Debug ChromaDB contents and document indexing."""
    print("=== DEBUG CHROMADB CONTENTS ===")

    try:
        # Initialize AI service
        ai_service = AIAnalysisService()

        # Get all data from ChromaDB
        print("\n1. CHECKING CHROMADB COLLECTION:")
        collection_data = ai_service.vectorstore.get()

        print(f"Total documents in ChromaDB: {len(collection_data.get('ids', []))}")
        print(f"Collection name: {ai_service.vectorstore._collection.name}")

        # Show all document IDs stored
        if collection_data.get('metadatas'):
            document_ids = set()
            for metadata in collection_data['metadatas']:
                if 'document_id' in metadata:
                    document_ids.add(metadata['document_id'])

            print(f"Document IDs found in ChromaDB: {sorted(document_ids)}")

            # Show chunks for each document
            for doc_id in sorted(document_ids):
                print(f"\n--- DOCUMENT {doc_id} CHUNKS ---")
                doc_filter = {"document_id": str(doc_id)}
                doc_chunks = ai_service.vectorstore.get(where=doc_filter)

                print(f"Chunks for document {doc_id}: {len(doc_chunks.get('ids', []))}")

                # Show first chunk content
                if doc_chunks.get('documents'):
                    print(f"First chunk preview: {doc_chunks['documents'][0][:200]}...")

                    # Show metadata
                    if doc_chunks.get('metadatas'):
                        print(f"Metadata: {doc_chunks['metadatas'][0]}")

        print("\n2. TESTING DOCUMENT RETRIEVAL:")

        # Test document 14 specifically
        doc_repo = DjangoDocumentRepository()
        document_14 = doc_repo.find_by_id(14)

        if document_14:
            print(f"\nDocument 14 found: {document_14.name}")
            print(f"PDF URL: {document_14.url_pdf}")
            print(f"Processing status: {document_14.processing_status}")
            print(f"Checksum: {document_14.checksum}")

            # Check if indexed
            is_indexed = ai_service._is_document_indexed(14)
            print(f"Document 14 indexed: {is_indexed}")

            # Show all chunks for this document
            doc_filter = {"document_id": 14}
            doc_chunks = ai_service.vectorstore.get(where=doc_filter)
            print(f"\nTotal chunks for document 14: {len(doc_chunks.get('ids', []))}")

            if doc_chunks.get('documents'):
                print("\n=== ALL CHUNKS CONTENT ===")
                for i, chunk in enumerate(doc_chunks['documents']):
                    print(f"\n--- CHUNK {i+1} ---")
                    print(f"Content: {chunk[:300]}...")
                    if i < len(doc_chunks.get('metadatas', [])):
                        print(f"Metadata: {doc_chunks['metadatas'][i]}")

            # Test different queries
            queries = [
                "experiência profissional trabalho",
                "projetos desenvolvidos",
                "habilidades técnicas",
                "certificações",
                "currículo profissional"
            ]

            print(f"\n=== TESTING DIFFERENT QUERIES ===")
            retriever = ai_service.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 5,  # Get more chunks
                    "filter": {"document_id": 14}
                }
            )

            for query in queries:
                print(f"\n--- Query: '{query}' ---")
                results = retriever.get_relevant_documents(query)
                print(f"Retrieved {len(results)} chunks:")

                for i, doc in enumerate(results):
                    print(f"  Chunk {i+1}: {doc.page_content[:100]}...")

        else:
            print("Document 14 not found!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chroma_contents()