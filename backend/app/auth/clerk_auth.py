import os
import requests
import time
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import SessionLocal
from app.models.models import User
import traceback

# Clerk Settings from Config
CLERK_FRONTEND_API = settings.CLERK_FRONTEND_API.replace("https://", "").replace("http://", "").rstrip("/")
CLERK_PEM_URL = f"https://{CLERK_FRONTEND_API}/.well-known/jwks.json"

security = HTTPBearer()

class ClerkUser(BaseModel):
    user_id: str
    role: Optional[str] = "member"
    email: Optional[str] = None
    name: Optional[str] = None
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    orders_shipped: Optional[str] = None

# Cache for Clerk Public Keys (JWKS)
_clerk_jwks: Optional[Dict[str, Any]] = None

def get_clerk_jwks():
    global _clerk_jwks
    if _clerk_jwks is None:
        if not settings.CLERK_FRONTEND_API:
            print("CRITICAL ERROR: CLERK_FRONTEND_API is not set in environment variables!")
            return {"keys": []}
            
        clean_api = settings.CLERK_FRONTEND_API.replace("https://", "").replace("http://", "").rstrip("/")
        jwks_url = f"https://{clean_api}/.well-known/jwks.json"
        
        try:
            print(f"DEBUG: Fetching Clerk JWKS from: {jwks_url}")
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            _clerk_jwks = response.json()
            print("DEBUG: Successfully fetched Clerk JWKS")
        except Exception as e:
            print(f"ERROR fetching Clerk JWKS from {jwks_url}: {e}")
            return {"keys": []}
    return _clerk_jwks

def sync_user_with_database(db: Session, clerk_user_id: str, email: Optional[str], role: str = "member", metadata: Dict = {}):
    """
    Ensures the user exists in the local database and has the latest metadata.
    """
    try:
        user = db.query(User).filter(User.id == clerk_user_id).first()
        
        name = metadata.get("name")
        company_name = metadata.get("company_name")
        phone_number = metadata.get("phone_number")
        orders_shipped = metadata.get("orders_shipped")

        if not user:
            new_user = User(
                id=clerk_user_id,
                email=email,
                name=name,
                company_name=company_name,
                phone_number=phone_number,
                orders_shipped=orders_shipped,
                role=role
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"SYNC: Provisioned user {clerk_user_id} with company: {company_name}")
            return True 
        else:
            updated = False
            if role and user.role != role:
                user.role = role
                updated = True
            if email and user.email != email:
                user.email = email
                updated = True
            if name and user.name != name:
                user.name = name
                updated = True
            if company_name and user.company_name != company_name:
                user.company_name = company_name
                updated = True
            if phone_number and user.phone_number != phone_number:
                user.phone_number = phone_number
                updated = True
            if orders_shipped and user.orders_shipped != orders_shipped:
                user.orders_shipped = orders_shipped
                updated = True
            
            if updated:
                db.commit()
                db.refresh(user)
                print(f"SYNC: Updated user {clerk_user_id} with company: {company_name}")
            
            return False
    except Exception as e:
        print(f"SYNC ERROR: {e}")
        db.rollback()
        return False

# Admin emails whitelist - Now dynamically updated from environment
_hardcoded_admins = ["worshipgate1@gmail.com", "shivam@theaffordableorganicstore.com", "naiknikhil248@gmail.com"]
_env_admins = [e.strip().lower() for e in settings.ANALYTICS_ALLOWED_EMAILS.split(",") if e.strip()]
ADMIN_EMAILS = list(set(_hardcoded_admins + _env_admins))

async def get_current_user(
    background_tasks: BackgroundTasks,
    auth: HTTPAuthorizationCredentials = Depends(security)
) -> ClerkUser:
    """
    Verifies the Clerk JWT and extracts user info.
    """
    token = auth.credentials
    jwks = get_clerk_jwks()
    
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key.get("kty"),
                    "kid": key.get("kid"),
                    "n": key.get("n"),
                    "e": key.get("e"),
                }
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token header")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # Extract metadata from JWT
        public_metadata = payload.get("public_metadata", {})
        unsafe_metadata = payload.get("unsafe_metadata", {})
        metadata = {**unsafe_metadata, **public_metadata}
        
        # FORCE Fallback to Clerk API if metadata seems incomplete
        if (not metadata.get("company_name") or not email) and settings.CLERK_SECRET_KEY:
            try:
                print(f"DEBUG: Metadata or email missing from JWT, fetching from Clerk API for {user_id}")
                clerk_url = f"https://api.clerk.com/v1/users/{user_id}"
                headers = {"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
                resp = requests.get(clerk_url, headers=headers)
                if resp.ok:
                    data = resp.json()
                    if not email:
                        email_addresses = data.get("email_addresses", [])
                        primary_email_id = data.get("primary_email_address_id")
                        for email_obj in email_addresses:
                            if email_obj.get("id") == primary_email_id:
                                email = email_obj.get("email_address")
                                break
                        if not email and email_addresses:
                            email = email_addresses[0].get("email_address")
                    
                    api_public_metadata = data.get("public_metadata", {})
                    api_unsafe_metadata = data.get("unsafe_metadata", {})
                    metadata = {**metadata, **api_unsafe_metadata, **api_public_metadata}
            except Exception as e:
                print(f"CLERK API FALLBACK ERROR: {e}")

        role = metadata.get("role", "member")

        # Database Check & Sync
        db = SessionLocal()
        try:
            sync_user_with_database(
                db=db,
                clerk_user_id=user_id,
                email=email,
                role=role,
                metadata=metadata
            )
            
            db_user = db.query(User).filter(User.id == user_id).first()
            if db_user:
                email = db_user.email or email
                role = db_user.role or role
                name = db_user.name or metadata.get("name")
                company_name = db_user.company_name or metadata.get("company_name")
                phone_number = db_user.phone_number or metadata.get("phone_number")
                orders_shipped = db_user.orders_shipped or metadata.get("orders_shipped")
            else:
                name = metadata.get("name")
                company_name = metadata.get("company_name")
                phone_number = metadata.get("phone_number")
                orders_shipped = metadata.get("orders_shipped")
        finally:
            db.close()

        # Hardcoded Admin Check
        if email in ADMIN_EMAILS:
            role = "admin"
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")

        return ClerkUser(
            user_id=user_id, 
            role=role, 
            email=email,
            name=name,
            company_name=company_name,
            phone_number=phone_number,
            orders_shipped=orders_shipped
        )

    except JWTError as e:
        print(f"JWT Verification Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_admin(current_user: ClerkUser = Depends(get_current_user)) -> ClerkUser:
    """
    Dependency that ensures the current user has an 'admin' role.
    """
    if current_user.email in ADMIN_EMAILS or current_user.role == "admin":
        return current_user
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Admin role required."
    )
