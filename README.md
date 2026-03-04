# HomeHQ — Secure Household Management System

A fully offline, air-gapped household management system built with Django 5+ and SQLite.

## Quick Start

### First Time Setup

```bash
# 1. Install Python dependencies (one-time)
pip install django

# 2. Run database migrations (one-time)
python manage.py migrate

# 3. Create your admin user (one-time)
python manage.py createsuperuser

# 4. Start the server
python manage.py runserver
```

Then open: **http://localhost:8000**

Default credentials (if using sample data): `admin` / `homehq2024`

---

## Features

| Module | Description |
|--------|-------------|
| **Finance → Bills** | Track recurring bills, one-click mark paid, auto-advance due date |
| **Finance → Budgets** | Monthly budget categories with spending progress bars |
| **Assets** | Inventory of high-value items with insurance linkage |
| **Assets → Loss Report** | Printable asset summary for insurance claims |
| **Garage** | Fleet tracking, maintenance logs, oil change alerts |
| **Notes** | Markdown knowledge base with tags and categories |

---

## Backup

```bash
# Backup to project directory
python manage.py backup_data

# Backup to USB drive
python manage.py backup_data --dest /media/usb/HomeHQ_Backups
```

---

## Air-Gap Compliance

- ✅ Zero CDN dependencies — Bootstrap and Chart.js are bundled in `/static/`
- ✅ No external API calls
- ✅ System fonts only (no Google Fonts)
- ✅ Single-file SQLite database (`db.sqlite3`)
- ✅ Local authentication only (no OAuth)

---

## Configuration

Edit `homehq/settings.py` for:
- `TIME_ZONE` — Set to your local timezone
- `SECRET_KEY` — Change before production use
- `ALLOWED_HOSTS` — Add your machine's hostname/IP

---

## Production Deployment (LAN)

```bash
# Collect static files
python manage.py collectstatic

# Run on your local network
python manage.py runserver 0.0.0.0:8000
```

Then access from any device on your LAN at `http://<your-ip>:8000`

---

## Running with Waitress (Recommended)

HomeHQ uses [Waitress](https://docs.pylonsproject.org/projects/waitress/) as its production WSGI server — a pure-Python, zero-dependency server that works perfectly in air-gapped environments.

```bash
# Local access only (default)
python serve.py

# Allow access from other devices on your LAN
python serve.py --host 0.0.0.0

# Custom port and thread count
python serve.py --host 0.0.0.0 --port 8080 --threads 8
```

Environment variable overrides also work:
```bash
HOMEHQ_HOST=0.0.0.0 HOMEHQ_PORT=8080 python serve.py
```
