import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "models/gemini-flash-latest"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Base directory for persistent data
    DATA_DIR: str = os.getenv("PERSISTENT_DATA_DIR", "backend")
    
    # Use absolute paths for the database to avoid issues with working directories
    @property
    def DATABASE_URL(self) -> str:
        db_path = os.path.abspath(os.path.join(self.DATA_DIR, "app.db"))
        return f"sqlite:///{db_path}"

    DOCS_DIR: str = os.path.join("backend", "data", "sops")
    INDEX_DIR: str = os.path.join(DATA_DIR, "faiss_index")

    TOP_K: int = 8
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 150

    SECRET_KEY: str = "change-me-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    ANALYTICS_ALLOWED_EMAILS: str = ""
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    PORT: int = 8000

    @property
    def allowed_emails(self) -> List[str]:
        return [e.strip() for e in self.ANALYTICS_ALLOWED_EMAILS.split(",") if e.strip()]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

