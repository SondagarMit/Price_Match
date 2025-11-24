#!/bin/bash
# Production startup script for Price Scraper

# Set environment to production
export ENVIRONMENT=production
export HOST=0.0.0.0
export PORT=${PORT:-8000}

# Start the server
cd api
uvicorn main:app --host $HOST --port $PORT --workers 4

