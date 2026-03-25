import asyncio
import os
import sys

# Setup paths
sys.path.append("backend")

from app.api.chat import chat_endpoint, ChatRequest
from app.auth.clerk_auth import ClerkUser, sync_user_with_database
from app.db import SessionLocal
from app.rag.retriever import Retriever
from app.rag.generator import Generator

async def test_chat():
    db = SessionLocal()
    # Updated ClerkUser to match current definition
    user_id = 'user_3AmwsWWcGF3fCb45LaIjc5SycSi'
    email = 'singhanurag.og49@gmail.com'
    role = 'member'
    company_name = 'Test Company'
    
    # MANUALLY SYNC USER (to simulate what get_current_user now does)
    print("Syncing user...")
    sync_user_with_database(
        clerk_user_id=user_id,
        email=email,
        role=role,
        metadata={"company_name": company_name}
    )

    user = ClerkUser(
        user_id=user_id, 
        role=role, 
        email=email,
        company_name=company_name
    )
    req = ChatRequest(query='What are the shipping rates?')
    
    retriever = Retriever()
    generator = Generator()
    
    print("Starting chat test...")
    try:
        # BackgroundTasks is required by get_current_user but chat_endpoint doesn't use it directly in its signature anymore
        # Wait, chat_endpoint uses ClerkUser from Depends(get_current_user), so we can pass it manually.
        from fastapi import BackgroundTasks
        # bg = BackgroundTasks() # Not needed if we call chat_endpoint directly with mock data
        
        response = await chat_endpoint(req, user, db, retriever, generator)
        print("Response received successfully!")
        print(response)
    except Exception as e:
        print("\n--- ERROR DETECTED ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat())
