from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.db import get_db
from app.auth.clerk_auth import get_current_user, ClerkUser, require_admin
from app.models.models import User, ChatLog, QueryFeedback
from app.core.config import settings
from typing import List

router = APIRouter()

@router.get("/admin/debug")
def get_admin_debug(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    """
    Minimal debug endpoint for admin testing.
    """
    total_users = db.query(func.count(User.id)).scalar()
    total_queries = db.query(func.count(ChatLog.id)).scalar()
    
    recent = (
        db.query(ChatLog)
        .order_by(ChatLog.timestamp.desc())
        .limit(5)
        .all()
    )
    
    recent_queries = [
        {
            "email": q.email,
            "company": q.company_name or "Unknown",
            "question": q.query_text,
            "created_at": q.timestamp.isoformat()
        }
        for q in recent
    ]
    
    return {
        "total_users": total_users,
        "total_queries": total_queries,
        "recent_queries": recent_queries
    }

@router.get("/top-queries")
def get_top_queries(
    range: str = Query("weekly", regex="^(weekly|monthly)$"),
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    days = 7 if range == "weekly" else 30
    start_date = datetime.utcnow() - timedelta(days=days)
    
    top_results = (
        db.query(
            ChatLog.query_text,
            func.count(ChatLog.id).label("count")
        )
        .filter(ChatLog.timestamp >= start_date)
        .group_by(ChatLog.query_text)
        .order_by(func.count(ChatLog.id).desc())
        .limit(15)
        .all()
    )
    
    final_results = []
    for rank, (query_text, count) in enumerate(top_results, 1):
        log_ids = db.query(ChatLog.id).filter(ChatLog.query_text == query_text).all()
        log_id_list = [l[0] for l in log_ids]
        
        likes = db.query(func.count(QueryFeedback.id)).filter(and_(
            QueryFeedback.query_log_id.in_(log_id_list),
            QueryFeedback.feedback_type == "like"
        )).scalar()
        
        dislikes = db.query(func.count(QueryFeedback.id)).filter(and_(
            QueryFeedback.query_log_id.in_(log_id_list),
            QueryFeedback.feedback_type == "dislike"
        )).scalar()
        
        total_feedback = likes + dislikes
        pos_pct = 0
        neg_pct = 0
        
        if total_feedback > 0:
            pos_pct = round((likes / total_feedback) * 100)
            neg_pct = round((dislikes / total_feedback) * 100)
            
        final_results.append({
            "rank": rank,
            "query": query_text,
            "count": count,
            "positive_percent": pos_pct if total_feedback > 0 else None,
            "negative_percent": neg_pct if total_feedback > 0 else None,
            "total_feedback": total_feedback
        })
    
    return {
        "range": range,
        "top_queries": final_results
    }

@router.get("/query-log/monthly")
def get_monthly_query_log(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    start_date = datetime.utcnow() - timedelta(days=30)
    
    # Query ChatLog and join with User for fallback data
    results = (
        db.query(
            ChatLog.query_text,
            ChatLog.timestamp,
            ChatLog.email,
            ChatLog.company_name,
            QueryFeedback.feedback_type,
            User.company_name.label("user_company"),
            User.email.label("user_email")
        )
        .outerjoin(QueryFeedback, ChatLog.id == QueryFeedback.query_log_id)
        .outerjoin(User, ChatLog.user_id == User.id)
        .filter(ChatLog.timestamp >= start_date)
        .order_by(ChatLog.timestamp.desc())
        .limit(100)
        .all()
    )
    
    logs = []
    for r in results:
        # Use ChatLog data first, fallback to User data if it's missing or "Unknown"
        email = r[2] or r[6] or "Unknown"
        company = r[3]
        if not company or company == "Unknown":
            company = r[5] or "Unknown"

        logs.append({
            "query": r[0],
            "timestamp": r[1].isoformat(),
            "email": email,
            "company": company,
            "feedback": r[4]
        })
        
    return {"logs": logs}

@router.get("/sop-missed")
def get_sop_missed_queries(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    results = (
        db.query(
            ChatLog.query_text,
            ChatLog.timestamp,
            ChatLog.email,
            ChatLog.company_name,
            User.company_name.label("user_company"),
            User.email.label("user_email")
        )
        .outerjoin(User, ChatLog.user_id == User.id)
        .filter(ChatLog.response_status == "not_found")
        .order_by(ChatLog.timestamp.desc())
        .limit(100)
        .all()
    )
    
    logs = []
    for r in results:
        email = r[2] or r[5] or "Unknown"
        company = r[3]
        if not company or company == "Unknown":
            company = r[4] or "Unknown"

        logs.append({
            "query": r[0],
            "timestamp": r[1].isoformat(),
            "email": email,
            "company": company
        })
        
    return {"logs": logs}

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users
