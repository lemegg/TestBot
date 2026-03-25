# Current Project State

## Features Implemented
- Clerk Authentication (Login/Signup)
- Customer-facing Chatbot
- User Metadata Form (Name, Company, Phone)
- RAG System (Gemini + pgvector)
- Admin Role (Hardcoded email: worshipgate1@gmail.com)
- Basic Admin Dashboard (Users list, Query list)
- Knowledge Base / Documents page with Upload UI (Admin Only)
- Document Upload to Cloudflare R2 and Processing pipeline
- Fixed backend admin auth mismatch causing 403 (Added synchronous Clerk API fallback for email verification)
- Chat endpoint made global (no user filtering, all users access shared knowledge base)
- Chat endpoint stabilized (no 500 errors)
- Added safe fallbacks + step-by-step debug logging
- Document retrieval ensured to always return a list
- Safe user metadata extraction implemented
- Vector store initialization validation added
- Fixed Clerk login UI layout (centered and styled)
- Company name now stored in chat logs and correctly shown in admin analytics

## What Works
- Login/Logout
- PDF/Docx Ingestion & Retrieval
- Chat logging (`chat_logs` table)
- Admin identification via hardcoded email
- Admin Debug Dashboard fetching from `/api/admin/debug`
- Console logs in frontend for chat verification

## Pending
- None (Core minimal testing system complete)

## TEST FLOW
1. Open incognito → login as customer
2. Fill metadata form
3. Ask 2 questions
4. Login as admin
5. Visit /api/admin/debug
6. Confirm:
   - queries exist
   - email + company visible
