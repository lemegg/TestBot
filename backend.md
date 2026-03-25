# Backend Instructions

## Environment Setup
Ensure you have the required dependencies installed:
```bash
pip install -r requirements.txt
```

## Running the Backend
To start the backend server, navigate to the root directory and run:

```powershell
$env:PYTHONPATH = (Join-Path $pwd "backend")
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

The server will be available at `http://localhost:8001`.

## API Documentation
Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Current Status
- **Started on:** 16 March 2026
- **Port:** 8001
- **Process ID:** (Background process)
