# API Routes

## Auth
- `GET /auth/me` - Get current user info

## Users
- `GET /api/user/users` - List all users (Admin only)

## Chat
- `POST /api/chat` - Send a message to the bot

## Documents
- `GET /api/docs` - List all documents (Admin only)
- `POST /api/docs/upload` - Upload a new document (Admin only)
- `DELETE /api/docs/{doc_id}` - Delete a document (Admin only)

## Analytics
- `GET /api/analytics/top-queries` - Get top queries (Admin only)
- `GET /api/analytics/query-log/monthly` - Monthly query logs (Admin only)
- `GET /api/analytics/sop-missed` - Queries with no results (Admin only)

## Admin (New)
- `GET /api/admin/debug` - Summary stats and 5 most recent queries
