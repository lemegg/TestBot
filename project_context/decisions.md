# Architectural Decisions

## Admin Identification
- **Hardcoded Emails**: Admins are identified by `worshipgate1@gmail.com`, `shivam@theaffordableorganicstore.com`, and `naiknikhil248@gmail.com`.
- **Simplification**: Removed organization and department-based logic to focus on a direct customer-to-admin model.

## Data Storage
- **Neon PostgreSQL**: Using pgvector for similarity search.
- **Clerk Metadata**: Storing company name and phone number in Clerk `publicMetadata` and syncing to local DB.
- **Email Handling**: Email is managed exclusively by Clerk. It is displayed as a read-only field in the Profile Metadata form to ensure users know which account they are updating without allowing manual changes that would break authentication consistency.

## RAG Pipeline
- **Embeddings**: Google Gemini `text-embedding-004`.
- **Generation**: Google Gemini Pro.
- **Storage**: Cloudflare R2 for source files.
