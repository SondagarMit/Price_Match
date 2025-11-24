"""FastAPI server for price scraper web app."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import scrapers (these are class definitions)
from scraper import (
    AmazonScraper,
    FlipkartScraper,
    MyntraScraper,
    AjioScraper,
)

# Environment config
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
DEBUG = ENVIRONMENT == "development"
HOST = os.getenv("HOST", "127.0.0.1" if DEBUG else "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000" if DEBUG else "*"
).split(",")

app = FastAPI(title="Price Scraper API", version="1.0.0", debug=DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve web directory if present
web_dir = os.path.join(BASE_DIR, "web")
if os.path.isdir(web_dir):
    app.mount("/static", StaticFiles(directory=web_dir), name="static")

# Thread pool for blocking scrapers
executor = ThreadPoolExecutor(max_workers=6)

# instantiate scrapers
SCRAPERS = {
    "amazon": AmazonScraper(),
    "flipkart": FlipkartScraper(),
    "myntra": MyntraScraper(),
    "ajio": AjioScraper(),
}

PLATFORM_STATUS = {
    "amazon": "implemented",
    "flipkart": "coming_soon",
    "myntra": "coming_soon",
    "ajio": "coming_soon",
}


@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(BASE_DIR, "web", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Price Scraper</h1><p>Frontend not found.</p>")


@app.get("/api")
async def api_root():
    return {"message": "Price Scraper API", "version": "1.0"}


@app.get("/api/platforms")
async def get_platforms():
    return {
        "platforms": [
            {"name": p, "status": PLATFORM_STATUS.get(p, "unknown"), "available": PLATFORM_STATUS.get(p) == "implemented"}
            for p in SCRAPERS.keys()
        ]
    }


@app.get("/api/scrape")
async def api_scrape(platform: str = Query(...), url: str = Query(...)):
    platform = platform.lower()
    if platform not in SCRAPERS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    if PLATFORM_STATUS.get(platform) != "implemented":
        raise HTTPException(status_code=501, detail=f"{platform} scraper not implemented yet")

    # Run blocking scrape in thread pool
    scraper = SCRAPERS[platform]

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(executor, scraper.scrape, url)
        return {"success": True, "platform": platform, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@app.get("/scrape")
async def scrape_alias(platform: str = Query(...), url: str = Query(...)):
    return await api_scrape(platform=platform, url=url)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, reload=DEBUG)
