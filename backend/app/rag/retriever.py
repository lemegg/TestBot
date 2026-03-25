from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.rag.embedder import Embedder
from app.rag.vector_search import search_chunks
from app.core.config import settings
import uuid

class Retriever:
    def __init__(self):
        self.embedder = Embedder()

    def retrieve(self, db: Session, query: str, top_k: int = settings.TOP_K) -> List[Dict[str, Any]]:
        """
        Embed the query and search for similar chunks in PostgreSQL.
        """
        query_embedding = self.embedder.get_embedding(query)
        # Convert to list for pgvector-python compatibility if needed
        query_embedding_list = query_embedding.tolist()
        
        # New vector search using pgvector
        results = search_chunks(db, query_embedding_list, limit=top_k)
        
        # Structure the results to match what the generator expects
        import json
        formatted_results = []
        for res in results:
            metadata = res.get("metadata")
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            elif metadata is None:
                metadata = {}
                
            formatted_results.append({
                "text": res["content"],
                "sop_name": metadata.get("document_name") or metadata.get("sop_name", "Unknown Document"),
                "section": metadata.get("section", "N/A")
            })
        
        return formatted_results
