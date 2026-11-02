# AI handoff — New Star Tailor

Updated: 2 November 2026. Give this file and the repository to Claude or another
coding assistant. This is project context, not a claim that every future change
has been approved. Read the user's current request and `AGENTS.md` first.

## Current source and deployment

- Canonical project: `/home/shyam/Documents/Work/newstartailor`.
- Repository: `https://github.com/Arya13819/New-Star-Tailor`; branch `shyam`.
- Website: `https://newstartailor.itgurujan.com`.
- Hostinger shared hosting, production PHP **8.3.36**, MySQL.
- All application files live under
  `/domains/itgurujan.com/public_html/newstartailor/` by the owner's preference.
- Standard Laravel folders are directly at project root. Root `index.php`
  delegates to `public/index.php`; root `.htaccess` maps assets and blocks private
  directories. Every private directory also carries its own deny `.htaccess`.
- No Node/Vite build is needed. Upload current source using FileZilla; preserve
  production `.env`, `storage/`, photos, APP_KEY and database.
- Database has already been imported on the live server. Do not reimport the
  full schema or run destructive migrations as part of a design update.
- `vendor/` exists locally for upload but is not tracked. A new Git clone needs
  `composer install` (or production `--no-dev --optimize-autoloader`).

## What has been completed

1. Original Flask/SQLAlchemy project was imported and redesigned on `shyam`.
2. The shop identity was rebuilt from its real signboard: red/black faceted star,
   used in the navigation, footer, receipts and PWA branding.
3. Responsive WebP photos, forest-green/ivory/gold design and lightweight CSS
   perspective effects were added. Services use live database prices and filters.
4. About/Contact embed maps at `24.4570252,74.870045`; phone is `9424035393`.
5. Hostinger shared hosting required a PHP implementation. The final application
   is Laravel 13, with Composer runtime dependencies locked for PHP 8.3.36.
6. Customer/staff login, orders, measurement versions, photos, payments,
   tracking, receipts, enquiries, reports and queued notifications were ported.
7. Source was consolidated into one standard Laravel folder. PHP views were
   converted to Blade and the dispatcher was split into named controllers.
8. GitHub `shyam` was pushed and verified at baseline commit `a62062e`.
9. The latest design refresh adds `atelier.css`, a bilingual homepage fit guide,
   refined cards/hero surfaces, mobile Call/Order shortcuts and a new static cache
   version. README and FileZilla guidance are maintained with this handoff.

Old Flask/native-PHP/upload variants are preserved locally under
`/home/shyam/Documents/Work/_newstartailor_archive/`; do not edit or deploy those.

## Architecture and important conventions

| Concern | Location |
| --- | --- |
| Laravel routes and role middleware | `routes/web.php` |
| Shared response/session/error wrapper | `app/Http/Controllers/TailoringController.php` |
| Storefront, enquiries and tracking | `PublicController.php` |
| Setup, signup/login/logout | `AuthController.php` |
| New orders/details/reference photos | `OrderController.php` |
| Customer portal | `CustomerController.php` |
| Staff CRUD, status, payments and reports | `AdminController.php` |
| Transactional business operations | `app/Tailoring/services.php` |
| Money/input/view/storage helpers | `app/Tailoring/bootstrap.php` |
| Shared request guards/system endpoints | `app/Tailoring/controllers.php` |
| Authentication model | `app/Models/User.php` |
| Roles/security headers | `app/Http/Middleware/` |
| Bilingual HTML templates | `resources/views/` |
| Shared shell | `resources/views/layouts/app.blade.php` |
| Static frontend | `public/static/`, `public/assets/` |

Laravel owns authentication, cookies, session, CSRF, requests and view rendering.
Existing domain operations deliberately use PDO obtained from Laravel's DB
connection, with explicit transactions and snapshots. This is not a complete
Eloquent rewrite. Do not claim otherwise or replace precision/ownership checks
with a shortcut. Shared helpers use namespace `App\Tailoring`; views currently
start with that namespace so helpers/constants resolve correctly.

`SessionState` stores shop UI state inside the Laravel session. The base
controller prepares locale/current-user/config state, catches redirect/status
signals and rolls back transactions on errors. Requests must pass through this
wrapper and the role middleware. Do not introduce standalone PHP endpoints that
bypass authentication/CSRF. No native `session_start` is needed.

## Business rules to preserve

- Men's tailoring only; shirt/trouser, Police, CRPF and Army categories.
- Cloth and stitching are separate line amounts.
- Customer fabric: required advance is 50% of stitching (rounded to paise).
  Shop fabric: required advance is 100% of the total. Missing advance warns;
  it does not automatically block the order workflow.
- Staff can quote unpriced services and urgent jobs. Online orders can only
  select active services with confirmed prices; ignore tampered client prices.
- Statuses: `NEW`, `MEASUREMENT`, `READY`, `DELIVERED`.
- Order numbers `NST-0001` onward come from a locked sequence row. Preserve
  atomic creation and durable duplicate-submission protection.
- Prices/service names and measurement versions are snapshotted per order.
  Catalogue edits must not change previous orders.
- Use integer paise for calculations and DECIMAL storage, not floating-point money.
- Partial verified payments are allowed. Cash/UPI recording and online manual
  verification must preserve existing authorization, overpayment and duplicate
  verification checks. Reports count verified payments only.
- Payment webhook returns 501 while unconfigured; it must never auto-verify a
  transaction. No live gateway or outbound SMS provider is configured.
- Self-entered measurements require acknowledgement; decimal measurements work.
- Customers only see their own orders/receipts/photos. Do not infer ownership
  from matching phone numbers. Customer mobile is not necessarily unique;
  account mobile is unique.
- Reference uploads are private, validated image files stored in
  `storage/app/private/references`; serve them only through authorized routes.
- First administrator requires a private setup key; setup locks after creation.
  Preserve bcrypt compatibility with existing Python `$2b$` hashes.

## Frontend editing notes

Keep English and Hindi content in sync. Escape user-supplied output with Blade
`{{ }}`. Only use raw output for trusted, already escaped helper HTML. No invented
reviews, customer counts or business history. Keep map coordinates and shop phone.
Use existing photos, local Bootstrap and CSS rather than adding heavy libraries.
Respect reduced motion, mobile widths, image dimensions and lazy loading. New
CSS is versioned in the shared layout and service-worker precache; bump cache
keys when changing cached assets so live visitors receive the update.

## Tests and environment

Previous consolidation passed 112 HTTP/MySQL checks, 6 PHPUnit tests (9 assertions),
responsive browser checks at 320/390/768/1440px, and Apache routing/private-file
checks. Re-run checks appropriate to the files you change; previous results are
not proof for a new modification. Local QA PHP is 8.4.27; production is 8.3.36.
Keep PHP 8.3 syntax/dependency compatibility.

```sh
php artisan test
vendor/bin/pint --dirty --format agent
```

The Python HTTP suite needs requests, PyMySQL and python-dotenv. It uses
`NST_PHP_TEST=1`, optional `NST_TEST_ENV`, a local `*_test` DB and port 5058.
Never point it at production. No QA credentials belong in Git. The existing
working `.env` contains hosting credentials; use a separate QA env file.
Do not publish passwords, setup/encryption keys, GitHub tokens, logs, sessions or
customer photos. Tokens previously shared in chat are not project configuration.

## Continuing work

Make focused changes in this canonical project, run relevant checks and commit
to `shyam` when requested. Preserve the user's live data during FileZilla updates.
If FTP credentials are unavailable, provide the exact changed-file upload list;
do not claim the site was deployed. Distinguish local checks, GitHub push and
actual server upload in the handoff. For this visual release no DB migration or
vendor change is required. Read `FILEZILLA_SETUP_HINDI.md` for update/rollback steps.

## Verification for this design refresh

PHPUnit: 6 tests, 9 assertions passed. Blade view cache compilation and JavaScript
syntax checks passed. Responsive browser verification passed at 320, 390, 768 and
1440px, including customer signup/login/logout and mobile order submission.
The new visual layer is about 7 KB of uncompressed CSS; no new runtime dependency,
SQL migration or vendor update is required for this release.
