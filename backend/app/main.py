from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.analytics import router as analytics_router
from app.models.models import Base
from app.core.database import engine
from app.core.config import settings
import os

# Initialize database
Base.metadata.create_all(bind=engine)

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
