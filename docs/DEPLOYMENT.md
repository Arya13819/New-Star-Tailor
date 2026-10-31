# Deployment

## Render (current target)

The repo includes `render.yaml` — Render reads this automatically ("Blueprint")
and provisions both the web service and a managed Postgres database in one go.

1. On [render.com](https://render.com), **New → Blueprint**, connect the
   `Arya13819/New-Star-Tailor` GitHub repo. Render finds `render.yaml` and
   shows a preview of what it's about to create (one web service, one
   Postgres database) — confirm it.
2. Render builds (`pip install` + `pybabel compile`) and deploys
   automatically. `DATABASE_URL`, `SECRET_KEY` and the production cookie
   flag are already wired up via `render.yaml` — nothing to type in by hand.
3. Still need to set manually, in the service's **Environment** tab (these
   are real secrets/business values — never put them in `render.yaml`,
   which is committed to the repo):
   - `SMS_API_KEY` / `SMS_SENDER_ID` — once an SMS provider is chosen
   - `PAYMENT_PROVIDER_KEY` / `PAYMENT_PROVIDER_SECRET` — once a payment
     provider is chosen
4. First deploy's `startCommand` already runs `flask db upgrade` and
   `nst seed-services` before Gunicorn starts — the database comes up with
   the full schema and default service catalogue with no extra step.
5. Create the first real admin account from Render's **Shell** tab (paid
   plans) or by running it locally once against the production
   `DATABASE_URL`:
   ```bash
   DATABASE_URL="<paste the external connection string from Render>" \
     flask --app wsgi nst create-admin
   ```
6. **Custom domain**: Render → service → **Settings → Custom Domains** → add
   the domain, then create the DNS record it shows you (usually a CNAME) at
   wherever the domain was bought. Render issues the HTTPS certificate
   automatically once DNS resolves — no separate Let's Encrypt step needed.
7. Verify: `/healthz`, `flask nst check` (via the Shell tab), the PWA/SEO
   checklist in step 11 of the general steps below, and that
   `Content-Security-Policy`/`Strict-Transport-Security` headers are present.
8. **Free-tier limitations worth knowing**: the free web service spins down
   after a period of inactivity (the first request after that takes ~30-60s
   to wake it back up), and the free Postgres database is **deleted after
   30 days** unless upgraded to a paid instance — take this seriously once
   there's real shop data in it (see `BACKUP.md`), or upgrade before that
   matters.

## General (any VPS — Nginx + Gunicorn)

Target: **Gunicorn + Nginx + Postgres/MySQL**, HTTPS only. Useful if moving
off Render later, or self-hosting instead.

## Overview
```
Browser ──HTTPS──> Nginx ──proxy──> Gunicorn (wsgi:app) ──> Postgres/MySQL
                     │
                     └── serves /static directly
```

## Steps
1. Provision a Linux server; install Python 3.11+, Postgres (or MySQL/MariaDB), Nginx.
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
    (only fire once `SMS_API_KEY`/`SMS_SENDER_ID` are set — see
    `Config.messaging_configured()`). Plain SMS only, never WhatsApp — an
    Indian SMS gateway needs a DLT-registered sender ID and templates
    before sending works.
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
`SMS_API_KEY`/`SMS_SENDER_ID`.
