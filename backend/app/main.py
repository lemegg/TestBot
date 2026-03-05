from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.analytics import router as analytics_router
from app.api.feedback import router as feedback_router
from app.models.models import Base
from app.core.database import engine
from app.core.config import settings
import os

# Initialize database
Base.metadata.create_all(bind=engine)

# Auto-ingest if index is missing or out of sync
def check_and_ingest():
    from app.rag.ingest import Ingestor
    from app.rag.vector_store import VectorStore
    
    should_ingest = False
    
    # 1. Check if index folder is empty or doesn't exist
    if not os.path.exists(settings.INDEX_DIR) or not os.listdir(settings.INDEX_DIR):
        print("FAISS index not found. Starting auto-ingestion...")
        should_ingest = True
    else:
        # 2. Check if the number of files in DOCS_DIR matches what's in the index
        try:
            vs = VectorStore()
            vs.load()
            indexed_files = set([m.get('sop_name') for m in vs.metadata])
            current_files = set([f for f in os.listdir(settings.DOCS_DIR) if f.lower().endswith(('.pdf', '.docx', '.txt'))])
            
            # 2a. Check for missing files
            if not current_files.issubset(indexed_files):
                print(f"New files detected in {settings.DOCS_DIR}. Updating index...")
                should_ingest = True
            
            # 2b. Check if we need to upgrade to the new link-extraction logic
            # If we have PDFs but no chunks mention 'Links found on this page', the index is old
            has_pdf = any(f.lower().endswith('.pdf') for f in current_files)
            has_link_logic = any("Links found on this page:" in m.get('text', '') for m in vs.metadata)
            
            if has_pdf and not has_link_logic:
                print("Index found but lacks link context. Forcing re-ingestion for high-fidelity extraction...")
                should_ingest = True
        except Exception as e:
            print(f"Error checking index status: {e}. Forcing re-ingestion just in case.")
            should_ingest = True

    if should_ingest:
        try:
            ingestor = Ingestor()
            ingestor.run()
            print("Auto-ingestion complete.")
        except Exception as e:
            print(f"Auto-ingestion failed: {e}")

check_and_ingest()

app = FastAPI(title="RAG Chatbot")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_ORIGIN,
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["feedback"])

# Serve the built React frontend
frontend_path = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {"message": "API is running. Frontend build not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
