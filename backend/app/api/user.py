from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models.models import User
from app.auth.clerk_auth import get_current_user, ClerkUser, require_admin
from pydantic import BaseModel
import uuid

router = APIRouter()

class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    orders_shipped: Optional[str] = None
    role: str
    
    class Config:
        from_attributes = True

@router.get("/me")
async def get_me(current_user: ClerkUser = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(require_admin)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users
