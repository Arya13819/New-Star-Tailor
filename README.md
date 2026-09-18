# New Star Tailor

Tailoring management website + PWA for **New Star Tailor**, Old UCO Bank Gully,
Near Patel Plaza, Tagore Marg, Neemuch, Madhya Pradesh — phone **9352672795**.

It replaces the shop's paper diary: customers, measurements (versioned), orders,
payments, receipts, reports, a customer portal and (later) WhatsApp
notifications. Scope is **men's tailoring only**.

> Business logic is authoritative in **[docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md)** — read it first.

## Stack
Flask · SQLAlchemy + Flask-Migrate · MySQL/MariaDB · Bootstrap 5 · Flask-Babel
(English + Hindi) · Flask-Login · pytest. Server-rendered, mobile-first,
installable PWA.

## Status — Phase 6 of 18 complete

| ✔ | Phase 1 | App factory, config, extensions, health checks, base UI, error pages |
| ✔ | Phase 2 | 14 SQLAlchemy models, initial Alembic migration, decimal money helpers, model tests |
| ✔ | Phase 3 | Admin + customer authentication, role-gated routes, rate-limited login, `flask nst create-admin` |
| ✔ | Phase 4 | Admin customer CRUD, search (name/mobile), duplicate-mobile warning (not a block), audit log |
| ✔ | Phase 5 | Measurement versioning UI — inches, fitting preference, history, pre-fill from last version |
| ✔ | Phase 6 | Service catalogue & pricing — `/admin/services`, seeded defaults, unset prices flagged not guessed |
| … | 7–18 | Orders, payments, dashboard, customer portal, online orders, receipts, notifications, reports, i18n, PWA, hardening, tests |

> **Local DB:** running on real **MariaDB 11.8** (`nst_dev` / `nst_test`) as of
> 2026-09-18 — see `docs/DATABASE_SETUP.md`. The SQLite fallback used during
> early phases still works out of the box if `DATABASE_URL` is ever unset.

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
```

The app runs **without** a database (health shows `degraded`); you need MySQL
from Phase 2 onward for migrations and the full test suite.

## Tests & lint

```bash
.venv/bin/pytest
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
