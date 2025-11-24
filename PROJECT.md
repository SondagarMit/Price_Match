# Project Overview – Price Scraper Web App

## 📖 Description
A lightweight **FastAPI** backend that scrapes product details from e‑commerce sites (currently Amazon) using **Requests** + **BeautifulSoup**. A simple static **HTML/JS** frontend lets users paste a product URL, choose a platform, and view the scraped data.

## 📂 Directory Structure
```
vector-pioneer/
│
├─ api/                # FastAPI server
│   └─ main.py          # API routes, scraper registry, static mount
│
├─ scraper/            # Modular scraper package
│   ├─ __init__.py
│   ├─ base_scraper.py  # abstract BaseScraper
│   ├─ amazon_scraper.py
│   ├─ flipkart_scraper.py   # placeholder
│   ├─ myntra_scraper.py     # placeholder
│   └─ ajio_scraper.py       # placeholder
│
├─ web/                # Front‑end (static files)
│   ├─ index.html
│   └─ script.js
│
├─ requirements.txt    # Python dependencies
└─ README.md           # Quick start guide (existing)
```

## ⚙️ Setup & Installation
```bash
# Clone / navigate to the project root
cd C:\Users\ADMIN\.gemini\antigravity\playground\vector-pioneer

# Install Python dependencies
pip install -r requirements.txt
```

## 🚀 Running the Server
```bash
# From the `api` directory
cd api
uvicorn main:app --reload
```
The API will be available at **http://127.0.0.1:8000**.

## 🌐 Front‑end Usage
Open a browser and go to **http://127.0.0.1:8000/**. The page shows:
- **Platform** selector (Amazon enabled, others marked *coming soon*)
- **Product URL** input field
- **Search** button
When you click **Search**, the UI calls `/scrape` and displays:
- Title
- Price
- Rating
- Image
- Availability
- Short description

## 📡 API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root – returns a friendly JSON message |
| `GET` | `/platforms` | Lists supported platforms and which are implemented |
| `GET` | `/scrape?platform=<platform>&url=<url>` | Scrapes the given product URL and returns a JSON payload. Errors return appropriate HTTP status codes. |

## 🛠️ Scraper Architecture
- **BaseScraper** (`scraper/base_scraper.py`) defines the abstract `scrape(url)` method and common utilities (user‑agents, text cleaning).
- **AmazonScraper** implements the concrete logic for Amazon India pages using CSS selectors.
- **Placeholder scrapers** (`flipkart_scraper.py`, `myntra_scraper.py`, `ajio_scraper.py`) return a *coming‑soon* error response.

## 📈 Future Enhancements
- Implement real scrapers for Flipkart, Myntra, Ajio.
- Add caching / rate‑limiting handling.
- Replace the static UI with a modern framework (React/Vite) if needed.
- Add unit tests for each scraper.

---
*All code lives under the `vector-pioneer` workspace. Feel free to modify or extend any component.*
