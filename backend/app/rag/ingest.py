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
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                
                # Extract hyperlinks with their positions
                hyperlinks = page.hyperlinks
                
                if hyperlinks:
                    # Sort links by their vertical position (top to bottom)
                    # This helps in inserting them close to the text they belong to
                    processed_text = page_text
                    
                    # We'll try to find the words associated with the link box
                    # This is advanced: we'll append a map of "Link Context" at the end of the page
                    link_map = []
                    for link in hyperlinks:
                        if not link.get('uri'): continue
                        
                        # Find words within the link's bounding box
                        link_bbox = (link['x0'], link['top'], link['x1'], link['bottom'])
                        words_in_link = page.within_bbox(link_bbox).extract_text()
                        
                        if words_in_link:
                            link_map.append(f"[{words_in_link.strip()}]({link['uri']})")
                        else:
                            # Fallback if no text inside box
                            link_map.append(link['uri'])
                    
                    if link_map:
                        page_text += "\n\nLinks found on this page:\n" + "\n".join(link_map)
                
                full_text += page_text + "\n\n"
        
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
