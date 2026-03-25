from backend.app.db import SessionLocal
from backend.app.models.models import Chunk, Document
import json

def check():
    db = SessionLocal()
    try:
        chunks = db.query(Chunk).limit(10).all()
        result = []
        for c in chunks:
            result.append({
                "org": c.organization_id,
                "dept": str(c.department_id) if c.department_id else None,
                "doc_id": str(c.document_id)
            })
        print("Chunks (First 10):", json.dumps(result, indent=2))
        
        docs = db.query(Document).all()
        doc_result = []
        for d in docs:
            doc_result.append({
                "name": d.name,
                "org": d.organization_id,
                "dept": str(d.department_id) if d.department_id else None
            })
        print("Documents:", json.dumps(doc_result, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    check()
