import os
import docx
import pdfplumber
from typing import List, Dict, Any
from app.rag.chunker import Chunker
from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Ingestor:
    def __init__(self):
        self.chunker = Chunker()
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def parse_docx(self, file_path: str) -> List[Dict[str, Any]]:
        doc = docx.Document(file_path)
        filename = os.path.basename(file_path)
        
        full_text = []
        current_section = "General"
        
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading'):
                current_section = para.text.strip()
            
            if para.text.strip():
                full_text.append((current_section, para.text.strip()))

        sections_content = {}
        for section, text in full_text:
            if section not in sections_content:
                sections_content[section] = []
            sections_content[section].append(text)
            
        all_chunks = []
        for section, texts in sections_content.items():
            section_text = "\n".join(texts)
            metadata = {
                "sop_name": filename,
                "section": section
            }
            chunks = self.chunker.chunk_document(section_text, metadata)
            all_chunks.extend(chunks)
            
        return all_chunks

    def parse_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        filename = os.path.basename(file_path)
        full_text = ""
        links_data = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # 1. Extract regular text
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                
                # 2. Extract hyperlinks
                page_links = page.hyperlinks
                if page_links:
                    for link in page_links:
                        if link.get('uri'):
                            links_data.append(link['uri'])
        
        # 3. Append links to text so they are indexed and visible to AI
        if links_data:
            full_text += "\n--- Document Links ---\n"
            # Remove duplicates while keeping order
            unique_links = []
            for l in links_data:
                if l not in unique_links:
                    unique_links.append(l)
            full_text += "\n".join(unique_links)
        
        metadata = {
            "sop_name": filename,
            "section": "General"
        }
        return self.chunker.chunk_document(full_text, metadata)

    def parse_txt(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        filename = os.path.basename(file_path)
        metadata = {
            "sop_name": filename,
            "section": "General"
        }
        return self.chunker.chunk_document(text, metadata)

    def run(self):
        logger.info(f"Scanning directory: {settings.DOCS_DIR}")
        all_processed_chunks = []
        
        for file in os.listdir(settings.DOCS_DIR):
            file_path = os.path.join(settings.DOCS_DIR, file)
            if file.endswith(".docx"):
                logger.info(f"Processing DOCX: {file}")
                all_processed_chunks.extend(self.parse_docx(file_path))
            elif file.endswith(".pdf"):
                logger.info(f"Processing PDF: {file}")
                all_processed_chunks.extend(self.parse_pdf(file_path))
            elif file.endswith(".txt"):
                logger.info(f"Processing TXT: {file}")
                all_processed_chunks.extend(self.parse_txt(file_path))
        
        if not all_processed_chunks:
            logger.warning("No documents found to index.")
            return

        logger.info(f"Embedding {len(all_processed_chunks)} chunks...")
        texts = [c["text"] for c in all_processed_chunks]
        embeddings = self.embedder.get_embeddings(texts)
        
        logger.info("Adding to FAISS index...")
        self.vector_store.add_embeddings(embeddings, all_processed_chunks)
        
        logger.info(f"Saving index to {settings.INDEX_DIR}")
        self.vector_store.save()
        logger.info("Ingestion complete.")

if __name__ == "__main__":
    ingestor = Ingestor()
    ingestor.run()
