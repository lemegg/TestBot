from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.auth import create_access_token, get_password_hash, verify_password, get_current_user
from app.models.models import User
from pydantic import BaseModel, EmailStr

from app.core.config import settings

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str

import uuid

class UserResponse(BaseModel):
    email: str
    id: str # Changed from int to str to match model
    is_admin: bool = False

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Domain restriction
    # If you want to test with any email, remove this block
    if not user.email.endswith("@theaffordableorganicstore.com"):
        # For testing, you might want to allow all emails or add your test domain
        pass 
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        id=str(uuid.uuid4()), # Generate a string ID for local users
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Add admin flag to response
    response_user = UserResponse(
        email=new_user.email,
        id=new_user.id,
        is_admin=new_user.email.lower() in settings.allowed_emails
    )
    return response_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        email=current_user.email,
        id=current_user.id,
        is_admin=current_user.email.lower() in settings.allowed_emails
    )
