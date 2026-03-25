import os
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

# Load .env explicitly from the root project directory
# Since this file is in backend/app/core/config.py, we look two levels up
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"), override=True)

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "models/gemini-1.5-flash"
    EMBEDDING_MODEL_NAME: str = "models/text-embedding-004"
    EMBEDDING_DIMENSION: int = 768
    
    # Base directory for persistent data
    DATA_DIR: str = os.getenv("PERSISTENT_DATA_DIR", "backend")
    
    # Use environment variable for DATABASE_URL if present, otherwise default to local SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{os.path.abspath(os.path.join('backend', 'app.db'))}")

    DOCS_DIR: str = os.path.join("backend", "data", "sops")
    INDEX_DIR: str = os.path.join(DATA_DIR, "faiss_index")

    # Cloudflare R2
    R2_ACCESS_KEY: str = os.getenv("R2_ACCESS_KEY", "")
    R2_SECRET_KEY: str = os.getenv("R2_SECRET_KEY", "")
    R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "")
    R2_CUSTOM_DOMAIN: str = os.getenv("R2_CUSTOM_DOMAIN", "")

    TOP_K: int = 4
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 150

    SECRET_KEY: str = "change-me-for-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    ANALYTICS_ALLOWED_EMAILS: str = ""
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    PORT: int = 8000

    # Clerk Auth
    CLERK_FRONTEND_API: str = os.getenv("CLERK_FRONTEND_API", "")
    CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")

    @property
    def allowed_emails(self) -> List[str]:
        # Handle cases where multiple emails are comma-separated or space-separated
        raw_list = self.ANALYTICS_ALLOWED_EMAILS.replace(' ', ',').split(',')
        return [e.strip().lower() for e in raw_list if e.strip()]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

