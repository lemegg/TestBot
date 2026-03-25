import io
import os
import uuid
import json
import requests
from sqlalchemy.orm import Session
from typing import Optional
from pypdf import PdfReader
from docx import Document as DocxDocument
import google.generativeai as genai

from app.db import SessionLocal
from app.models.models import Chunk, Document
from app.core.config import settings
from app.rag.cloud_storage import r2_storage
from app.ingestion.chunk_text import chunk_text

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_text(file_content: bytes, filename: str) -> str:
    """Extract text from PDF, DOCX, or TXT"""
    text = ""
    file_ext = os.path.splitext(filename)[1].lower()
    
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
        print(f"Extraction error for {filename}: {e}")
        
    return text.strip()

def process_document(document_id: uuid.UUID, file_url: str):
    """
    Main ingestion pipeline:
    1. Download from R2
    2. Extract text
    3. Chunk
    4. Generate Embeddings (Gemini)
    5. Store in Neon pgvector table
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            print(f"Document {document_id} not found in DB")
            return

        doc.status = 'processing'
        db.commit()

        print(f"Ingesting: {doc.name}")
        
        object_name = f"documents/{doc.name}"
        response = r2_storage.s3.get_object(Bucket=r2_storage.bucket_name, Key=object_name)
        file_content = response['Body'].read()

        # 2. Extract Text
        text = extract_text(file_content, doc.name)
        if not text:
            print(f"No text extracted from {doc.name}")
            doc.status = 'failed'
            db.commit()
            return

        # 3. Chunk Text
        chunks = chunk_text(text, chunk_size=800, overlap=150)
        print(f"Extracted {len(chunks)} chunks from {doc.name}")

        # 4. Generate Embeddings & 5. Store in Neon
        db_chunks = []
        for i, chunk_content in enumerate(chunks):
            result = genai.embed_content(
                model=settings.EMBEDDING_MODEL_NAME,
                content=chunk_content,
                task_type="retrieval_document",
                output_dimensionality=settings.EMBEDDING_DIMENSION
            )
            embedding = result['embedding']
            
            db_chunk = Chunk(
                document_id=document_id,
                content=chunk_content,
                embedding=embedding,
                metadata_json=json.dumps({
                    "chunk_index": i,
                    "document_name": doc.name
                })
            )
            db_chunks.append(db_chunk)

        # Batch insert
        db.add_all(db_chunks)
        
        doc.status = 'ready'
        db.commit()
        print(f"Successfully processed and stored {len(db_chunks)} chunks.")

    except Exception as e:
        db.rollback()
        # RE-FETCH doc if needed or use session
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = 'failed'
            db.commit()
        print(f"Pipeline error for {document_id}: {e}")
    finally:
        db.close()
