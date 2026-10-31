# Redesign verification — 31 October 2026

## Automated checks

```sh
TEST_DATABASE_URL='mysql+pymysql://USER:PASSWORD@HOST:PORT/nst_test?charset=utf8mb4' \
  .venv/bin/python -m pytest
```

Result: **197 passed** on an isolated MariaDB 11.8 database. The migration test
also explicitly exercises SQLite. Only use a dedicated disposable test database:
the suite creates and removes application tables.

The suite covers staff/customer authentication, role checks and customer data
isolation, measurements, order creation, payments, receipts, reports, enquiries,
notifications, SEO/PWA, dynamic catalogue prices and the current tracking step.

`python -m compileall -q app`, translation catalogue compilation and
`git diff --check` completed successfully.

## Browser checks

Checked with headless Chromium at 1440px and 390px widths using the actual Flask
server and MariaDB, with CSRF enabled:

- All public pages, both login pages and registration render successfully.
- Mobile navigation and representative forms have no horizontal overflow.
- Customer registration, sign out and subsequent sign in work.
- Online order creation and adding/removing service rows work.
- Customer order details display the saved order status.
- Staff login and dashboard work; moving an order to READY appears immediately
  in customer details and public tracking.
- Tracking with the wrong mobile number does not show the order result.
- No browser JavaScript errors were observed.

## Database delivery

Applied the full migration chain to an empty MariaDB database and seeded the
catalogue. Exported schema, service catalogue and revision only, then successfully
imported `database/new_star_tailor.sql` into a second empty database. `nst check`
reported 15 application tables and revision `2e3b1bebff15`; `db upgrade` after
import was a successful no-op. Customer/account/order tables in the delivered SQL
are empty. The optional Docker Compose service was not run (Docker unavailable).
MySQL 8 server itself was not available; database execution checks used MariaDB.

## Source provenance

Original code: supplied `New-Star-Tailor-main.zip`, whose archive comment records
upstream commit `3ed62554f1156763ed9bd81fecb464d490b99720`. The local repository
contains an original-source import commit and the redesign on branch `shyam`.
A ZIP does not include upstream Git history. No deployment was requested; this
handoff is source code and MySQL setup for the user's hosting environment.
