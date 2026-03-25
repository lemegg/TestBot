import tiktoken
from typing import List

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Splits text into chunks based on token count using tiktoken.
    Chunk size: 800 tokens
    Overlap: 150 tokens
    """
    # Use the appropriate encoding for Gemini models (cl100k_base is common for modern LLMs)
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    chunks = []
    
    # Start at 0, slide by chunk_size - overlap
    for i in range(0, len(tokens), chunk_size - overlap):
        # Extract token range
        chunk_tokens = tokens[i : i + chunk_size]
        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Stop if we've reached the end
        if i + chunk_size >= len(tokens):
            break
            
    return chunks
