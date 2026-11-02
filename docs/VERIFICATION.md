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

## Services catalogue and storefront identity — 31 October 2026

Redesigned services with an editorial photo header, category links, search,
result counts, pricing cards, native FAQ accordions and contextual order/call
actions. Filtering combines category and literal case-insensitive text search;
inactive services are excluded. Order links preselect only active priced
services on GET and never override submitted POST data.

Recreated the shop signboard's red/black faceted star as an 863-byte SVG. Updated
navigation, footer, receipts, favicon, Apple touch and regular/maskable PWA icons.
About now uses the real storefront with 480/960/1440px WebP sources. The 960px
version is 114,572 bytes compared with the original JPEG's 357,387 bytes. Originals
remain unchanged. The dedicated 13.8KB catalogue stylesheet loads only on Services
and About. No filtering library, image-generation dependency or extra runtime
JavaScript was introduced. The service-worker cache version is v6.

Chromium checks passed at 320, 390, 768, 1024 and 1440px on Home, Services and
About: no horizontal overflow, broken loaded images or JavaScript errors.
Verified combined category/search, reset and empty states, service-to-order
preselection and Hindi pages with JavaScript disabled. Automated release checks: **200 tests passed** on SQLite; Python compilation,
service-worker syntax and Git whitespace checks passed.

## Google Maps — 2 November 2026

Added the same responsive Google Maps card to About and Contact at the supplied
coordinates 24.4570252,74.870045, zoom 17. The card includes the shop address,
open-in-Maps and driving-directions links. Contact also has a refreshed contact
information layout. The map iframe lazy-loads, has an accessible title and reserved
height; location CSS loads only on these two pages. Frame permissions are scoped
to these two routes and the two Google Maps hostnames. Cache version is v7.

21 focused smoke, SEO/PWA and map tests passed, including exact coordinates,
iframe accessibility and scoped CSP. Chromium loaded the actual Google Maps embed
on both routes at 390px and 1440px: map tiles and the pin were visually verified,
with no horizontal overflow or page JavaScript errors. Python compilation,
service-worker syntax and Git whitespace checks passed.
