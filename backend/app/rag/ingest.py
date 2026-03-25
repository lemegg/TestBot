import io
import os
import uuid
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.rag.cloud_storage import r2_storage
from app.rag.chunker import Chunker
from app.rag.embedder import Embedder
from app.models.models import Chunk, Document
from app.core.config import settings
from pypdf import PdfReader
from docx import Document as DocxDocument
import requests

class Ingestor:
    def __init__(self, db: Session):
        self.db = db
        self.chunker = Chunker()
        self.embedder = Embedder()

    def process_document(self, document_id: uuid.UUID):
        """
        Full ingestion flow:
        1. Fetch document metadata
        2. Download from R2
        3. Extract text
        4. Chunk
        5. Embed
        6. Store
        """
        # 1. Fetch metadata
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            print(f"Document {document_id} not found in DB")
            return

        print(f"Processing document: {doc.name}")

        # 2. Download from R2
        try:
            object_name = f"documents/{doc.name}"
            response = r2_storage.s3.get_object(Bucket=r2_storage.bucket_name, Key=object_name)
            file_content = response['Body'].read()
        except Exception as e:
            print(f"Error downloading from R2: {e}")
            return

        # 3. Extract Text
        text = ""
        file_ext = os.path.splitext(doc.name)[1].lower()
        
        try:
            if file_ext == '.pdf':
                reader = PdfReader(io.BytesIO(file_content))
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            elif file_ext == '.docx':
                doc_obj = DocxDocument(io.BytesIO(file_content))
                for para in doc_obj.paragraphs:
                    text += para.text + "\n"
            else:
                # Assume plain text
                text = file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error extracting text: {e}")
            return

        if not text.strip():
            print("No text extracted from document")
            return

        # 4. Chunk
        metadata = {
            "document_id": str(doc.id),
            "document_name": doc.name
        }
        chunks_metadata = self.chunker.chunk_document(text, metadata)
        chunk_texts = [c["text"] for c in chunks_metadata]

        # 5. Embed
        print(f"Generating embeddings for {len(chunk_texts)} chunks...")
        # Note: Gemini embed_content has limits on batch size, but for typical SOPs it should be fine.
        # If very large, we might need to batch these calls.
        embeddings = self.embedder.get_embeddings(chunk_texts)

        # 6. Store in DB
        db_chunks = []
        for i, chunk_data in enumerate(chunks_metadata):
            db_chunk = Chunk(
                document_id=doc.id,
                content=chunk_data["text"],
                embedding=embeddings[i].tolist(),
                metadata_json=json.dumps({k: v for k, v in chunk_data.items() if k != "text"})
            )
            db_chunks.append(db_chunk)

        try:
            self.db.add_all(db_chunks)
            self.db.commit()
            print(f"Successfully ingested {len(db_chunks)} chunks for document {doc.name}")
        except Exception as e:
            self.db.rollback()
            print(f"Error saving chunks to DB: {e}")

def process_document_task(db: Session, document_id: uuid.UUID):
    ingestor = Ingestor(db)
    ingestor.process_document(document_id)
