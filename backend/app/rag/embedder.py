import google.generativeai as genai
import numpy as np
from typing import List
from app.core.config import settings

class Embedder:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings using Google Gemini API.
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type="retrieval_document",
                output_dimensionality=settings.EMBEDDING_DIMENSION
            )
            return np.array(result['embedding']).astype("float32")
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise e

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate a single embedding for a query.
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_query",
                output_dimensionality=settings.EMBEDDING_DIMENSION
            )
            return np.array(result['embedding']).astype("float32")
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise e
