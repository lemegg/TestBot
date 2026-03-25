from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.analytics import router as analytics_router
from app.api.feedback import router as feedback_router
from app.api.documents import router as documents_router
from app.models.models import Base
from app.db import engine
from app.core.config import settings
import os

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Chatbot")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    settings.FRONTEND_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(documents_router, prefix="/api/docs", tags=["documents"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["feedback"])

# Serve the built React frontend
frontend_path = os.path.join(os.getcwd(), "frontend", "dist")

if os.path.exists(frontend_path):
    # Serve static assets (js, css, etc.)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Catch-all for SPA: Serve index.html for any path not matched above
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "API is running. Frontend build not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)

