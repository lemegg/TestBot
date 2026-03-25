from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.models import Chunk
from pgvector.sqlalchemy import Vector
from typing import List, Dict, Any, Optional
import uuid

def search_chunks(db: Session, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a vector similarity search in PostgreSQL using pgvector.
    No longer filtering by organization/department as per new requirements.
    """
    # L2 distance (<->) search in SQLAlchemy with pgvector
    stmt = (
        select(Chunk)
        .order_by(Chunk.embedding.l2_distance(query_embedding))
        .limit(limit)
    )
    
    results = db.execute(stmt).scalars().all()
    
    return [
        {
            "content": chunk.content,
            "metadata": chunk.metadata_json,
            "document_id": str(chunk.document_id)
        }
        for chunk in results
    ]
