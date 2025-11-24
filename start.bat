@echo off
REM Windows startup script for Price Scraper (Development)

REM Set environment to development
set ENVIRONMENT=development
set HOST=127.0.0.1
set PORT=8000

REM Start the server
cd api
uvicorn main:app --host %HOST% --port %PORT% --reload

