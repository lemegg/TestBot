import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "models/gemini-flash-latest"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    DOCS_DIR: str = os.path.join("backend", "data", "sops")
    INDEX_DIR: str = os.path.join("backend", "faiss_index")
    TOP_K: int = 4
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 100

    SECRET_KEY: str = "change-me-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    DATABASE_URL: str = "sqlite:///./backend/app.db"

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

