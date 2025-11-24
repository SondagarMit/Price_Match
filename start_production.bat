@echo off
REM Windows startup script for Price Scraper (Production)

REM Set environment to production
set ENVIRONMENT=production
set HOST=0.0.0.0
set PORT=8000

REM Start the server
cd api
uvicorn main:app --host %HOST% --port %PORT% --workers 4

