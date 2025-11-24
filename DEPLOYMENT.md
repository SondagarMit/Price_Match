# Deployment Guide - Price Scraper

This guide explains how to deploy the Price Scraper application in both **localhost (development)** and **production (live)** environments.

## 🏠 Localhost Development

### Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run the development server:
   - **Windows**: Double-click `start.bat` or run `start.bat` in terminal
   - **Linux/Mac**: Run `chmod +x start.sh && ./start.sh`
   - **Manual**: `cd api && uvicorn main:app --reload`

3. Access at: `http://127.0.0.1:8000`

### Development Features
- ✅ Auto-reload on code changes
- ✅ Debug mode enabled
- ✅ Detailed error messages
- ✅ CORS allows localhost origins

## 🌐 Production Deployment

### Step 1: Environment Configuration

Create a `.env` file in the project root:

```env
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Important**: Replace `yourdomain.com` with your actual domain!

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start Production Server

**Option A: Using Scripts**
- **Windows**: Run `start_production.bat`
- **Linux/Mac**: `export ENVIRONMENT=production && ./start.sh`

**Option B: Manual Start**
```bash
cd api
export ENVIRONMENT=production
export HOST=0.0.0.0
export PORT=8000
export ALLOWED_ORIGINS=https://yourdomain.com
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Option C: Using Gunicorn (Recommended)**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
```

### Step 4: Reverse Proxy (Nginx Example)

If using Nginx, add this configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 5: SSL/HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d yourdomain.com
```

## 🔧 Environment Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `ENVIRONMENT` | `development` | `production` | Environment mode |
| `HOST` | `127.0.0.1` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | `8000` | Server port |
| `ALLOWED_ORIGINS` | `http://localhost:8000,...` | `https://yourdomain.com` | CORS allowed origins |

## 🚀 Platform-Specific Deployment

### Heroku
1. Create `Procfile`:
   ```
   web: uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
2. Set environment variables in Heroku dashboard
3. Deploy: `git push heroku main`

### Railway
1. Connect your repository
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### DigitalOcean App Platform
1. Connect repository
2. Configure environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Docker
1. Build: `docker build -t price-scraper .`
2. Run: `docker run -p 8000:8000 -e ENVIRONMENT=production price-scraper`

## ✅ Production Checklist

- [ ] Environment variables configured
- [ ] `ALLOWED_ORIGINS` set to your domain
- [ ] SSL/HTTPS enabled
- [ ] Multiple workers configured (4+ recommended)
- [ ] Firewall rules configured
- [ ] Monitoring/logging set up
- [ ] Backup strategy in place

## 🔍 Testing Production Locally

Test production mode on your local machine:

```bash
export ENVIRONMENT=production
export HOST=0.0.0.0
export ALLOWED_ORIGINS=http://localhost:8000
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

## 📝 Notes

- **Development**: Single worker, auto-reload, debug mode
- **Production**: Multiple workers, no auto-reload, optimized logging
- Always use HTTPS in production
- Configure CORS properly for security
- Use a process manager (PM2, systemd) for production

---

*For issues, check the main README.md troubleshooting section.*

