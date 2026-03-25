# Database Schema

## Users Table (`users`)
- `id` (String, PK) - Clerk user_id
- `email` (String, Unique)
- `name` (String)
- `company_name` (String)
- `phone_number` (String)
- `role` (String) - 'admin' or 'member'
- `created_at` (DateTime)

## Chat Logs Table (`chat_logs`)
- `id` (Integer, PK)
- `user_id` (String, FK)
- `email` (String)
- `company_name` (String)
- `query_text` (String) - The user's question
- `response_text` (String) - The bot's answer
- `timestamp` (DateTime)
- `retrieved_sop` (String) - Source document names
- `response_status` (String) - SUCCESS or not_found

## Chunks Table (`chunks`)
- `id` (UUID, PK)
- `document_id` (UUID)
- `content` (Text)
- `embedding` (Vector(768))
- `metadata_json` (Text)

## Documents Table (`documents`)
- `id` (UUID, PK)
- `name` (String)
- `storage_url` (String)
- `status` (String)
- `created_at` (DateTime)
