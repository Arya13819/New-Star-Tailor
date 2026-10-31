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

## Premium visual update — 31 October 2026

Added a dark forest-green hero, layered product photography, gold accents,
raised collection cards, a craftsmanship section and optional pointer-driven
CSS perspective. The effect script is 1,490 bytes, runs only on pointer input
through requestAnimationFrame, and skips touch devices and reduced-motion users.
No 3D libraries, WebGL, remote fonts or animation dependencies were added.

Responsive WebP product copies (320px/640px) use picture/srcset with JPEG fallbacks.
The nine original photos total 625,281 bytes; their 640px WebP copies total
266,324 bytes (57.4% smaller). Original photos are retained; regenerate the copies
with `.venv/bin/python scripts/optimize_images.py`. The hero loads eagerly and
other product photos load lazily. Styles and the enhancement script are versioned;
the PWA cache version was updated to v5.

Verification: 197 tests passed on SQLite. Chromium checks passed at 320, 390, 768,
1024 and 1440 pixels with no horizontal overflow or JavaScript errors. Confirmed
WebP selection, desktop pointer depth, mobile menu navigation, reduced-motion
behavior, the primary CTA with JavaScript disabled, public services/gallery,
login/tracking pages and the Hindi homepage. These are local checks, not a
production performance score or a hosting deployment.
