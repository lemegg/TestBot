from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth.clerk_auth import get_current_user, ClerkUser
from app.models.models import User, ChatLog, QueryFeedback
from pydantic import BaseModel, field_validator

router = APIRouter()

class FeedbackRequest(BaseModel):
    query_log_id: int
    feedback: str

    @field_validator('feedback')
    @classmethod
    def validate_feedback(cls, v: str) -> str:
        if v not in ('like', 'dislike'):
            raise ValueError('feedback must be "like" or "dislike"')
        return v

@router.post("")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure local user exists for foreign key constraints
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        user = User(
            id=current_user.user_id,
            email=current_user.email
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Check if query_log exists
    query_log = db.query(ChatLog).filter(ChatLog.id == request.query_log_id).first()
    if not query_log:
        raise HTTPException(status_code=404, detail="Query log not found")

    # Check for duplicate feedback
    existing_feedback = db.query(QueryFeedback).filter(
        QueryFeedback.query_log_id == request.query_log_id,
        QueryFeedback.user_id == user.id
    ).first()
    if existing_feedback:
        # Just update it instead of erroring out to be more user-friendly
        existing_feedback.feedback_type = request.feedback
        db.commit()
        return {"message": "Feedback updated"}

    # Create feedback
    new_feedback = QueryFeedback(
        query_log_id=request.query_log_id,
        user_id=user.id,
        feedback_type=request.feedback
    )
    db.add(new_feedback)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": "Feedback recorded"}
