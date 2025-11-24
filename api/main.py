"""FastAPI server for price scraper web app."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import scraper package
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scraper import (
    AmazonScraper,
    FlipkartScraper,
    MyntraScraper,
    AjioScraper,
)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
DEBUG = ENVIRONMENT == "development"
HOST = os.getenv("HOST", "127.0.0.1" if DEBUG else "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# CORS configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000" if DEBUG else "*"
).split(",")

app = FastAPI(
    title="Price Scraper API",
    version="1.0.0",
    debug=DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (HTML, JS, CSS)
web_dir = os.path.join(BASE_DIR, "web")
app.mount("/static", StaticFiles(directory=web_dir), name="static")

# Scraper registry
SCRAPERS = {
    'amazon': AmazonScraper(),
    'flipkart': FlipkartScraper(),
    'myntra': MyntraScraper(),
    'ajio': AjioScraper(),
}

# Platform implementation status
PLATFORM_STATUS = {
    'amazon': 'implemented',
    'flipkart': 'coming_soon',
    'myntra': 'coming_soon',
    'ajio': 'coming_soon',
}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    try:
        html_path = os.path.join(BASE_DIR, "web", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Frontend not found</h1><p>Please ensure web/index.html exists.</p>",
            status_code=404
        )


@app.get("/api")
async def api_root():
    """Root API endpoint."""
    return {
        "message": "Welcome to Price Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "platforms": "/api/platforms",
            "scrape": "/api/scrape?platform=<platform>&url=<url>"
        }
    }


@app.get("/api/platforms")
async def get_platforms():
    """List all supported platforms and their implementation status."""
    return {
        "platforms": [
            {
                "name": platform,
                "status": status,
                "available": status == "implemented"
            }
            for platform, status in PLATFORM_STATUS.items()
        ]
    }


@app.get("/api/scrape")
async def scrape_product(
    platform: str = Query(..., description="Platform name (amazon, flipkart, myntra, ajio)"),
    url: str = Query(..., description="Product URL to scrape")
):
    """
    Scrape product information from the given URL.
    
    Args:
        platform: Platform name (amazon, flipkart, myntra, ajio)
        url: Product URL to scrape
        
    Returns:
        JSON object with product information
    """
    # Validate platform
    platform = platform.lower()
    if platform not in SCRAPERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {platform}. Supported platforms: {list(SCRAPERS.keys())}"
        )
    
    # Check if platform is implemented
    if PLATFORM_STATUS.get(platform) != 'implemented':
        raise HTTPException(
            status_code=501,
            detail=f"{platform.capitalize()} scraper is coming soon! This feature is not yet implemented."
        )
    
    # Validate URL
    if not url or not url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Please provide a valid HTTP/HTTPS URL."
        )
    
    # Scrape the product
    try:
        scraper = SCRAPERS[platform]
        result = scraper.scrape(url)
        return {
            "success": True,
            "platform": platform,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )

