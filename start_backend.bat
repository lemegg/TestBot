@echo off
cd /d "c:\Users\Anurag\Desktop\Projects\RAG-New"
set PYTHONPATH=%cd%\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
