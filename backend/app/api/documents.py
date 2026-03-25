from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Document
from app.auth.clerk_auth import get_current_user, ClerkUser, require_admin
from app.rag.cloud_storage import r2_storage
from app.ingestion.process_document import process_document
import uuid
from typing import Optional

router = APIRouter()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    filename = file.filename
    # Flat storage path for now: documents/filename
    object_name = f"documents/{filename}"

    # 2. Upload file to Cloudflare R2
    try:
        success = r2_storage.upload_fileobj(file.file, object_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to upload file to R2")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"R2 Upload Error: {str(e)}")

    # 3. Generate storage URL
    storage_url = r2_storage.generate_presigned_url(object_name)

    # 4. Save metadata to Database
    new_doc = Document(
        id=uuid.uuid4(),
        name=filename,
        storage_url=storage_url
    )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # 5. Trigger Background Document Processing
    background_tasks.add_task(process_document, new_doc.id, storage_url)

    return {
        "document_id": str(new_doc.id),
        "url": storage_url,
        "status": new_doc.status
    }

@router.get("")
async def list_documents(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    docs = db.query(Document).all()
    return docs

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from R2
    object_name = f"documents/{doc.name}"
    r2_storage.delete_file(object_name)
    
    # Delete from Database
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully"}
