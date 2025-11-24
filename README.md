# Price Scraper Web App

A lightweight **FastAPI** backend that scrapes product details from e-commerce sites (currently Amazon) using **Requests** + **BeautifulSoup**. A modern **HTML/JS** frontend with Tailwind CSS lets users paste a product URL, choose a platform, and view the scraped data.

## 📂 Directory Structure

```
Price_comp/
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
├─ README.md           # This file
└─ PROJECT.md          # Project documentation
```

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Navigate to the project root**
   ```bash
   cd D:\Price_comp
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables (optional)**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env file with your settings (optional for development)
   # For production, you MUST configure this file
   ```

## 🚀 Running the Server

### Development Mode (Localhost)

**Option 1: Using the startup script (Windows)**
```bash
start.bat
```

**Option 2: Using the startup script (Linux/Mac)**
```bash
chmod +x start.sh
./start.sh
```

**Option 3: Manual start**
```bash
cd api
uvicorn main:app --reload
```

**Option 4: Direct Python execution**
```bash
cd api
python main.py
```

### Production Mode

**Option 1: Using the production startup script (Windows)**
```bash
start_production.bat
```

**Option 2: Using the production startup script (Linux/Mac)**
```bash
chmod +x start.sh
export ENVIRONMENT=production
./start.sh
```

**Option 3: Manual production start**
```bash
cd api
export ENVIRONMENT=production
export HOST=0.0.0.0
export PORT=8000
export ALLOWED_ORIGINS=https://yourdomain.com
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Configuration

The application supports both **development** and **production** environments through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Set to `production` for live deployment |
| `HOST` | `127.0.0.1` (dev) / `0.0.0.0` (prod) | Server host address |
| `PORT` | `8000` | Server port number |
| `ALLOWED_ORIGINS` | `http://localhost:8000,...` | Comma-separated list of allowed CORS origins |

**For Production:**
1. Create a `.env` file in the project root
2. Set `ENVIRONMENT=production`
3. Set `HOST=0.0.0.0` (to accept connections from any interface)
4. Set `ALLOWED_ORIGINS` to your domain(s), e.g., `https://yourdomain.com,https://www.yourdomain.com`
5. Use multiple workers for better performance: `--workers 4`

1. **Navigate to the api directory**
   ```bash
   cd api
   ```

2. **Start the FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```

   Or run directly:
   ```bash
   python main.py
   ```

3. **Access the application**
   - Frontend: **http://127.0.0.1:8000/**
   - API Root: **http://127.0.0.1:8000/api**
   - API Docs: **http://127.0.0.1:8000/docs** (Swagger UI)

## 🌐 Front‑end Usage

1. Open your browser and navigate to **http://127.0.0.1:8000/**
2. Select a platform from the dropdown (Amazon is currently available)
3. Paste a product URL in the input field
4. Click the **Search Product** button
5. View the scraped product information:
   - Product image
   - Title
   - Price
   - Rating
   - Availability
   - Description

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root – serves the HTML frontend |
| `GET` | `/api` | API root – returns API information |
| `GET` | `/api/platforms` | Lists supported platforms and which are implemented |
| `GET` | `/api/scrape?platform=<platform>&url=<url>` | Scrapes the given product URL and returns a JSON payload. Errors return appropriate HTTP status codes. |

### Example API Request

```bash
curl "http://127.0.0.1:8000/api/scrape?platform=amazon&url=https://www.amazon.in/dp/B08N5WRWNW"
```

### Example Response

```json
{
  "success": true,
  "platform": "amazon",
  "data": {
    "title": "Product Title",
    "price": 1299.00,
    "price_text": "₹1,299.00",
    "rating": 4.5,
    "rating_text": "4.5 out of 5 stars",
    "image": "https://...",
    "availability": "In Stock",
    "description": "Product description...",
    "url": "https://www.amazon.in/dp/..."
  }
}
```

## 🛠️ Scraper Architecture

- **BaseScraper** (`scraper/base_scraper.py`) defines the abstract `scrape(url)` method and common utilities (user‑agents, text cleaning, price/rating extraction).
- **AmazonScraper** implements the concrete logic for Amazon India pages using CSS selectors.
- **Placeholder scrapers** (`flipkart_scraper.py`, `myntra_scraper.py`, `ajio_scraper.py`) return a *coming‑soon* error response.

## 🎨 Frontend Features

- **Modern UI** with Tailwind CSS
- **Responsive design** that works on desktop and mobile
- **Real-time feedback** with loading indicators
- **Error handling** with user-friendly messages
- **Smooth animations** for better UX

## 📈 Future Enhancements

- Implement real scrapers for Flipkart, Myntra, Ajio
- Add caching / rate‑limiting handling
- Replace the static UI with a modern framework (React/Vite) if needed
- Add unit tests for each scraper
- Add product comparison feature
- Add price history tracking

## 🌍 Deployment

### Localhost vs Production

The application automatically adapts to the environment:

- **Localhost (Development)**: 
  - Runs on `127.0.0.1:8000`
  - Auto-reload enabled
  - CORS allows localhost origins
  - Debug mode enabled

- **Production (Live)**:
  - Runs on `0.0.0.0` (all interfaces)
  - Multiple workers for performance
  - CORS restricted to specified domains
  - Optimized logging

### Deployment Options

**1. Traditional VPS/Server:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENVIRONMENT=production
export HOST=0.0.0.0
export PORT=8000
export ALLOWED_ORIGINS=https://yourdomain.com

# Run with Gunicorn (recommended for production)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
```

**2. Docker (Optional):**
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**3. Cloud Platforms:**
- **Heroku**: Set environment variables in dashboard
- **Railway**: Configure via environment variables
- **DigitalOcean App Platform**: Use environment configuration
- **AWS/GCP/Azure**: Use their respective deployment services

## 🐛 Troubleshooting

### Port Already in Use
If port 8000 is already in use, you can specify a different port:
```bash
uvicorn main:app --reload --port 8001
```
Or set the `PORT` environment variable:
```bash
export PORT=8001
uvicorn main:app --reload
```

### CORS Errors in Production
If you see CORS errors when deploying:
1. Check your `ALLOWED_ORIGINS` environment variable
2. Ensure it includes your exact domain (with https://)
3. Restart the server after changing environment variables

### Import Errors
Make sure you're running the server from the `api` directory, or adjust the Python path in `main.py` if needed.

### Scraping Fails
- Ensure the product URL is valid and accessible
- Check that the website structure hasn't changed (scrapers may need updates)
- Verify your internet connection
- Some websites may block automated requests - consider using proxies or rotating user agents

## 📝 License

This project is open source and available for modification and extension.

---

*Happy Scraping! 🚀*

