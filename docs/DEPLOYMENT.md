# Deployment

Target: **Gunicorn + Nginx + MySQL/MariaDB**, HTTPS only.

## Overview
```
Browser ──HTTPS──> Nginx ──proxy──> Gunicorn (wsgi:app) ──> MySQL
                     │
                     └── serves /static directly
```

## Steps
1. Provision a Linux server; install Python 3.11+, MySQL/MariaDB, Nginx.
2. Create the app database and user — see `DATABASE_SETUP.md`.
3. Clone the repo, create a venv, `pip install -r requirements.txt`.
4. Create `/etc/new-star-tailor.env` (mode 600) from `.env.example` with:
   - a strong `SECRET_KEY`
   - `FLASK_ENV=production`
   - `SESSION_COOKIE_SECURE=true`
   - real `DATABASE_URL`
5. `flask --app wsgi db upgrade`.
6. `flask --app wsgi nst seed-services` for first-run service catalogue.
7. Compile translations: `pybabel compile -d app/translations` — required
   before every deploy; the `.mo` file is gitignored and rebuilt from the
   committed `.po`, so a forgotten compile silently ships English-only.
8. systemd unit runs `gunicorn -c gunicorn.conf.py wsgi:app`.
9. Nginx: TLS (Let's Encrypt), proxy to Gunicorn, serve `/static/` directly,
   cap `client_max_body_size` to match `MAX_UPLOAD_MB` (default 8 MB).
   **Must** set `X-Forwarded-Proto`, `X-Forwarded-Host` and
   `X-Forwarded-For` on the proxied request — the app wraps its WSGI stack
   in `ProxyFix` (`app/__init__.py`) and trusts exactly one hop of these
   headers to know it's being served over HTTPS. Without them, secure
   cookies, HSTS, and the canonical/Open Graph URLs silently regress to
   `http://` even though the site is actually on HTTPS.
10. Cron: `flask nst notifications process` and `flask nst reminders run`
    (only fire once `WHATSAPP_API_KEY`/`WHATSAPP_PHONE_ID` are set — see
    `Config.messaging_configured()`).
11. Verify the PWA + SEO surface once live: `/static/manifest.webmanifest`
    and `/sw.js` (both must resolve, `sw.js` at the site root, not under
    `/static/`, so its scope covers the whole site), `/robots.txt` and
    `/sitemap.xml` (must list only public pages), and confirm the
    `Content-Security-Policy` / `Strict-Transport-Security` response
    headers are present (`app/utils/headers.py`).
12. Run `flask nst check` after every deploy — confirms DB connectivity,
    schema revision, and whether payments/messaging are wired up.

## Secrets
Never in the repo. Environment file or a secrets manager only:
`SECRET_KEY`, `DATABASE_URL`, `PAYMENT_PROVIDER_KEY/SECRET`,
`WHATSAPP_API_KEY/PHONE_ID`.
