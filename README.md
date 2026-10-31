# New Star Tailor

Tailoring management website + PWA for **New Star Tailor**, Old UCO Bank Gully,
Near Patel Plaza, Tagore Marg, Neemuch, Madhya Pradesh — phone **9352672795**.

**Live:** https://new-star-tailor.onrender.com

It replaces the shop's paper diary: customers, measurements (versioned), orders,
payments, receipts, reports, a customer portal and (later) SMS
notifications. Scope is **men's tailoring only**.

> Business logic is authoritative in **[docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md)** — read it first.

## Redesign and MySQL handoff (`shyam`)

The refreshed site uses warm ivory, a dark forest-green hero, layered product
photography, subtle 3D depth, gold accents and raised collection cards. Optional
desktop pointer effects respect reduced-motion preferences. Responsive WebP
photographs reduce the 640px image set by 57% while retaining JPEG fallbacks. It includes a responsive storefront, clear mobile
navigation, customer/staff login screens, styled management views and a shared
order progress indicator on tracking and customer order details. Homepage prices
come from the active database catalogue instead of hardcoded rates.

**Database:** [database/new_star_tailor.sql](database/new_star_tailor.sql) can be
imported into an empty MySQL database or phpMyAdmin. Read
[database/README.md](database/README.md) for import, Docker, configuration and login
setup. Existing migrations and authentication are retained. No live database,
customer data or passwords are included in Git. See [verification](docs/VERIFICATION.md)
for the checks performed and environment limits.

## Stack
Flask · SQLAlchemy + Flask-Migrate · PostgreSQL (production, on Render) /
MySQL-MariaDB or SQLite (local dev) · Bootstrap 5 · Flask-Babel
(English + Hindi) · Flask-Login · pytest. Server-rendered, mobile-first,
installable PWA. Deployment: see `docs/DEPLOYMENT.md` (`render.yaml` deploys
the whole thing — app + Postgres — as a Render Blueprint).

## Status — Phase 18 of 18 complete

| ✔ | Phase 1 | App factory, config, extensions, health checks, base UI, error pages |
| ✔ | Phase 2 | 14 SQLAlchemy models, initial Alembic migration, decimal money helpers, model tests |
| ✔ | Phase 3 | Admin + customer authentication, role-gated routes, rate-limited login, `flask nst create-admin` |
| ✔ | Phase 4 | Admin customer CRUD, search (name/mobile), duplicate-mobile warning (not a block), audit log |
| ✔ | Phase 5 | Measurement versioning UI — inches, fitting preference, history, pre-fill from last version |
| ✔ | Phase 6 | Service catalogue & pricing — `/admin/services`, seeded defaults, unset prices flagged not guessed |
| ✔ | Phase 7 | Walk-in orders — `/admin/orders`, NST-0001 numbering, stitching/material split, manual urgent pricing, status lifecycle |
| ✔ | Phase 8 | Payments — partial payments, cash/UPI auto-verified vs online pending, overpayment blocked, provider abstraction, inert webhook |
| ✔ | Phase 9 | Admin dashboard — status counts, urgent/overdue/today's deliveries, outstanding balance, recent orders, quick actions, global search |
| ✔ | Phase 10 | Customer portal — own orders/measurements/payments only, strict per-customer data isolation (404, not 403, on a guessed id) |
| ✔ | Phase 11 | Online ordering — `/enquiry`, `/order` (self-measurement + ack, reference photo, pending payment intent), `/track-order`, `/admin/enquiries` |
| ✔ | Phase 12 | Printable order + payment receipts for admin and the customer portal (own orders only) |
| ✔ | Phase 13 | SMS-ready notifications (never WhatsApp) — order confirmation/ready hooks, `/admin/notifications`, `nst notifications process` + `nst reminders run` CLI (honest no-op until a provider is configured) |
| ✔ | Phase 14 | Reports — today/week/month/custom, category breakdown, revenue from verified payments only, live pending-payments list |
| ✔ | Phase 15 | Full Hindi translation — every form label, flash message and template string wrapped for i18n, 351-string `hi` catalogue, `?lang=hi` switch remembered in session |
| ✔ | Phase 16 | PWA — installable manifest + icon set, service worker caching only the static shell and read-only public pages (never admin/customer/API), `/sw.js` served at root scope |
| ✔ | Phase 17 | SEO + hardening — canonical/OG/Twitter tags, JSON-LD `ClothingStore` listing, `robots.txt` + `sitemap.xml` (public pages only), CSP with per-request nonce, HSTS, `X-Frame-Options`, `Permissions-Policy`, `ProxyFix` for correct HTTPS detection behind Nginx |
| ✔ | Phase 18 | Final hardening pass — 197 tests passing (redesign verification), `DEPLOYMENT.md`/`BACKUP.md` finalised for production |

> MySQL setup is environment-specific; see [database/README.md](database/README.md).

See the master plan for the full phase list.

## Quick start (development)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt

cp .env.example .env
# set SECRET_KEY:  python -c "import secrets; print(secrets.token_hex(32))"

# Optional now / required for MySQL — see docs/DATABASE_SETUP.md, then set
# DATABASE_URL + TEST_DATABASE_URL in .env. Leaving them blank uses SQLite.

.venv/bin/flask --app wsgi db upgrade        # create the schema
.venv/bin/flask --app wsgi nst check         # connectivity + schema revision
.venv/bin/flask --app wsgi nst create-admin  # first shop staff login
.venv/bin/flask --app wsgi nst seed-services # default service catalogue (idempotent)
.venv/bin/flask --app wsgi run --debug       # http://127.0.0.1:5000
# then: /admin/login (staff) · /admin/customers (customer + measurement management)
#       /admin/services (pricing — some prices are intentionally unset, see BUSINESS_RULES.md)
#       /customer/login or /customer/register (customers)
#       /enquiry · /order · /track-order (public, no login needed)
```

The app runs **without** a database (health shows `degraded`); you need MySQL
from Phase 2 onward for migrations and the full test suite.

## Tests & lint

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check .
```

## Layout

```
wsgi.py                 gunicorn / flask run entrypoint
gunicorn.conf.py        production server config
app/
  __init__.py           application factory
  config.py             env-driven configuration
  extensions.py         db, migrate, login, csrf, babel, limiter
  routes/               public / auth / customer_portal / admin / api
  services/             business logic (orders, pricing, payments, …)
  repositories/         data access
  models/               SQLAlchemy models
  forms/  utils/  templates/  static/  translations/
  cli.py                `flask nst …` commands
docs/                   BUSINESS_RULES · DATABASE_SETUP · DEPLOYMENT · BACKUP
tests/
```

## The old prototype

An earlier React + Convex prototype is preserved on the git branch
**`legacy/convex-prototype`** (`git show legacy/convex-prototype:README.md`).
`main` is the Flask rewrite.
