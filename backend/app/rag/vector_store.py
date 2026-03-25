import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.models import Chunk
import uuid
import json

class VectorStore:
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.pending_chunks = []

    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Prepare chunks for insertion into PostgreSQL.
        Metadata is expected to contain 'text' and other fields.
        """
        if embeddings.shape[0] != len(metadata):
            raise ValueError("Number of embeddings and metadata items must match.")
        
        for i in range(len(metadata)):
            chunk_metadata = metadata[i]
            doc_id = chunk_metadata.get("document_id", uuid.uuid4())
            
            chunk = Chunk(
                document_id=doc_id,
                content=chunk_metadata.get("text", ""),
                embedding=embeddings[i].tolist(),
                metadata_json=json.dumps({k: v for k, v in chunk_metadata.items() if k != "text"})
            )
            self.pending_chunks.append(chunk)

    def save(self):
        """
        Commit pending chunks to the PostgreSQL database.
        """
        if not self.pending_chunks:
            return
            
        try:
            self.db.add_all(self.pending_chunks)
            self.db.commit()
            print(f"Successfully saved {len(self.pending_chunks)} chunks to Postgres.")
            self.pending_chunks = []
        except Exception as e:
            self.db.rollback()
            print(f"Error saving to Postgres: {e}")
            raise e

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        """
        from app.rag.vector_search import search_chunks
        return search_chunks(self.db, query_embedding.tolist(), limit=top_k)

    def load(self, folder_path: str = None):
        """No-op for Postgres as it's always 'loaded'"""
        pass
