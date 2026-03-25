from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.rag.retriever import Retriever
from app.rag.generator import Generator
from app.auth.clerk_auth import get_current_user, ClerkUser
from app.models.models import ChatLog
from app.db import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()
_retriever: Optional[Retriever] = None
_generator: Optional[Generator] = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever

def get_generator():
    global _generator
    if _generator is None:
        _generator = Generator()
    return _generator

class Answer(BaseModel):
    summary: str
    steps: List[str]
    rules: List[str]
    notes: List[str]

class Source(BaseModel):
    sop: str
    section: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    query_log_id: int
    answer: Answer
    sources: List[Source]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    retriever: Retriever = Depends(get_retriever),
    generator: Generator = Depends(get_generator)
):
    try:
        # STEP 1: User OK
        print("STEP 1: User OK")
        
        # SAFE USER EXTRACTION
        company_name = getattr(current_user, 'company_name', None) or "Unknown"
        email = getattr(current_user, 'email', None) or "Unknown"
        
        print(f"CHAT USER: {email}")
        print(f"COMPANY: {company_name}")
        print(f"QUESTION: {request.query}")

        # STEP 2: Retrieving docs
        print("STEP 2: Retrieving docs")
        
        # VALIDATE VECTOR STORE INITIALIZATION
        if retriever is None:
            raise Exception("Retriever not initialized")

        # Retrieve chunks (no longer filtering by organization/department)
        # Ensure retriever ALWAYS returns a list
        docs = retriever.retrieve(db, request.query) or []
        
        # STEP 3: Docs count
        print(f"STEP 3: Docs count: {len(docs)}")

        # HANDLE EMPTY DOCS
        if len(docs) == 0:
            return ChatResponse(
                query_log_id=0,
                answer=Answer(
                    summary="I couldn't find relevant information in the knowledge base.",
                    steps=[],
                    rules=[],
                    notes=[]
                ),
                sources=[]
            )
        
        # STEP 4: Generating response
        print("STEP 4: Generating response")
        
        # Generate structured answer
        # The current generator.generate_answer uses self.model.generate_content which is equivalent to chain.invoke
        result = generator.generate_answer(request.query, docs)
        
        if result is None:
            result = {
                "answer": {
                    "summary": "No response generated.",
                    "steps": [],
                    "rules": [],
                    "notes": []
                },
                "sources": []
            }

        # Determine status
        answer_summary = result.get('answer', {}).get('summary', '')
        status = "SUCCESS"
        if not docs or "Information not found" in answer_summary:
            status = "not_found"

        # Log the query
        sop_names = list(set([str(c.get("sop_name", "Unknown")) for c in docs]))
        
        log = ChatLog(
            user_id=current_user.user_id,
            email=email,
            company_name=company_name,
            query_text=request.query,
            response_text=answer_summary,
            retrieved_sop=", ".join(sop_names) if sop_names else "NONE",
            response_status=status
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        print(f"CHAT_LOG: {email} | {company_name} | {request.query}")
        print("SAVED TO chat_logs")
        
        return ChatResponse(query_log_id=log.id, **result)

    except Exception as e:
        print("CHAT ERROR:", str(e))
        import traceback
        traceback.print_exc()
        # Return a graceful fallback instead of crashing with 500
        return ChatResponse(
            query_log_id=0,
            answer=Answer(
                summary="Something went wrong. Please try again.",
                steps=[],
                rules=[],
                notes=[f"Error: {str(e)}"]
            ),
            sources=[]
        )
