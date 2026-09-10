# Deployment (outline — filled in at Phase 18)

Target: **Gunicorn + Nginx + MySQL/MariaDB**, HTTPS only.

## Overview
```
Browser ──HTTPS──> Nginx ──proxy──> Gunicorn (wsgi:app) ──> MySQL
                     │
                     └── serves /static directly
```

## Steps (draft)
1. Provision a Linux server; install Python 3.11+, MySQL/MariaDB, Nginx.
2. Create the app database and user — see `DATABASE_SETUP.md`.
3. Clone the repo, create a venv, `pip install -r requirements.txt`.
4. Create `/etc/new-star-tailor.env` (mode 600) from `.env.example` with:
   - a strong `SECRET_KEY`
   - `FLASK_ENV=production`
   - `SESSION_COOKIE_SECURE=true`
   - real `DATABASE_URL`
5. `flask --app wsgi db upgrade` (Phase 2+).
6. `flask --app wsgi nst seed` for first-run services/settings (Phase 6+).
7. Compile translations: `pybabel compile -d app/translations` (Phase 15+).
8. systemd unit runs `gunicorn -c gunicorn.conf.py wsgi:app`.
9. Nginx: TLS (Let's Encrypt), proxy to Gunicorn, serve `/static/`, set
   `X-Forwarded-Proto`, cap `client_max_body_size` to match `MAX_UPLOAD_MB`.
10. Cron: `flask nst notifications process` and `flask nst reminders run`
    (Phase 13+).

## Secrets
Never in the repo. Environment file or a secrets manager only:
`SECRET_KEY`, `DATABASE_URL`, `PAYMENT_PROVIDER_KEY/SECRET`,
`WHATSAPP_API_KEY/PHONE_ID`.
