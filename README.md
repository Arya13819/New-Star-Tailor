# New Star Tailor

**Made to measure. Managed with care.**

A bilingual tailoring storefront and shop-management application for New Star
Tailor, Neemuch. Customers can explore services, place an order and follow its
progress; staff can manage measurements, payments and delivery from one place.

[Website](https://newstartailor.itgurujan.com) ·
[FileZilla deployment guide](FILEZILLA_SETUP_HINDI.md) ·
[AI / developer handoff](AI_HANDOFF.md)

| Platform | Details |
| --- | --- |
| Backend | Laravel 13, PHP target **8.3.36** |
| Database | MySQL / MariaDB |
| Templates | Laravel Blade, English and Hindi |
| Frontend | Bootstrap, custom CSS, lightweight JavaScript, responsive WebP |
| Hosting | Hostinger shared hosting; one subdomain folder |
| Development branch | `shyam` |

## About the website

**Live website: [https://newstartailor.itgurujan.com/](https://newstartailor.itgurujan.com/)**

New Star Tailor is a men's tailoring and uniform shop in Neemuch, Madhya Pradesh.
The website brings its shirt, trouser, Police, CRPF and Army tailoring services
online, with service prices, shop photographs, directions and direct contact.
Customers can register, place an order and track its progress. Staff use a
protected workspace to manage customers, measurements, orders and payments.

The site is built with Laravel and MySQL for Hostinger shared hosting, with
English/Hindi pages and a responsive design for phones and desktops. The current
production website is **newstartailor.itgurujan.com**; the previous Render address
is a legacy deployment.

## What the website does

- **Storefront:** editorial product photography, subtle CSS depth, searchable
  services with live catalogue prices, real shop identity and embedded maps.
- **Customer portal:** registration/login, orders, measurements, payments and
  receipts, with access restricted to the signed-in customer's own data.
- **Order workflow:** multiple services, fractional measurements, versioned
  measurement snapshots, reference photos and order-number/mobile tracking.
- **Shop workspace:** walk-in customers, catalogue edits, order status, payment
  verification, enquiries, receipts and revenue reports.
- **Practical mobile design:** responsive layouts, accessible focus states,
  reduced-motion support and storefront Call / Order shortcuts.

Money is calculated in integer paise and stored as decimal amounts. Catalogue
price changes do not rewrite past orders. Online payment references need manual
verification; a real payment gateway and outbound SMS provider are **not yet
configured**. Notification records currently form a queue.

## One project, one location

```text
/home/shyam/Documents/Work/newstartailor/
├── app/Http/Controllers/       # public, auth, order, customer and admin logic
├── app/Http/Middleware/        # roles and response security headers
├── app/Models/                # Laravel user authentication
├── app/Tailoring/             # shared business rules, helpers, translations
├── config/                    # framework and shop configuration
├── database/                  # schema, migration and catalogue seeder
├── public/                    # public entry point, CSS, JS, images and logo
├── resources/views/           # Blade HTML templates
│   ├── layouts/app.blade.php   # navigation, footer and shared page shell
│   ├── pages/                 # customer/admin/order views
│   ├── pages/marketing/       # English and Hindi marketing pages
│   └── partials/              # reusable sections
├── routes/web.php             # explicit Laravel routes and role groups
├── storage/                   # private photos, logs, sessions and cache
├── tests/                     # PHPUnit and guarded HTTP/MySQL verification
├── index.php                  # shared-hosting adapter to public/index.php
└── .env                       # private local/production settings; never in Git
```

The previous Flask project and experimental upload packages are archived locally
under `/home/shyam/Documents/Work/_newstartailor_archive/`. They are not part of
the current production source.

## Find the code you want to edit

| Change | File |
| --- | --- |
| Home/About/Contact/Gallery HTML | `resources/views/pages/marketing/en/` and `hi/` |
| Services catalogue | `resources/views/pages/services.blade.php` |
| New homepage fit guide | `resources/views/partials/fit-guide.blade.php` |
| Header, footer, mobile shortcuts | `resources/views/layouts/app.blade.php` |
| Latest visual finish | `public/static/css/atelier.css` |
| Existing design foundations | `public/static/css/theme.css`, `premium.css`, `catalogue.css` |
| Logo and photographs | `public/static/img/` |
| Login and signup | `app/Http/Controllers/AuthController.php` |
| Order creation and money rules | `app/Tailoring/services.php` |
| Staff management | `app/Http/Controllers/AdminController.php` |
| Database / shop settings | `.env`, `config/database.php`, `config/tailoring.php` |

No Node/Vite build is required for the storefront. Edit Blade/CSS/JS directly.
Keep English and Hindi pages in sync.

## Local setup

Use PHP >=8.3 with Composer, PDO MySQL and Laravel's standard extensions
(including mbstring, XML, curl and fileinfo), plus a separate local MySQL database.

```sh
composer install
```

For a **fresh clone**, copy `.env.example` to `.env`, configure your local MySQL
credentials, set `APP_URL=http://127.0.0.1:8000` and
`SESSION_SECURE_COOKIE=false`, then:

```sh
php artisan key:generate
php artisan migrate
php artisan serve --host=127.0.0.1 --port=8000
```

For initial admin creation, set `NST_SETUP_KEY` to a private random value of at
least 32 characters and open `/setup`. The setup route locks after the first
administrator. There is no default admin password.

**This existing working folder already contains hosting settings in its private
`.env`. Preserve them. Use a separate environment for local testing rather than
pointing tests at the live database. Never regenerate the live APP_KEY.**

## Verification

```sh
php artisan test
vendor/bin/pint --dirty --format agent
```

The HTTP/MySQL suite (`tests/http_edge_cases.py`) exercises real requests,
authentication, order amounts, uploads and customer isolation. It deliberately
requires `NST_PHP_TEST=1`, a local `*_test` database and the QA URL
`http://127.0.0.1:5058`. `NST_TEST_ENV` selects a private QA environment file.
Python test dependencies: requests, PyMySQL and python-dotenv. Never run this
suite against the production database.

## Update the live website with FileZilla

Local: **`/home/shyam/Documents/Work/newstartailor/`**

Remote: **`/domains/itgurujan.com/public_html/newstartailor/`**

Follow [the Hindi guide](FILEZILLA_SETUP_HINDI.md), especially its **existing live
site update** section. Upload only the changed source/assets for this design
release. **Do not replace `.env`, `storage/`, uploaded photos or the live database.**
There is no SQL import, schema migration or vendor update for the design refresh.

For a fresh installation only, build production dependencies locally with
`composer install --no-dev --optimize-autoloader`. Git excludes `vendor/`, so a
GitHub clone needs Composer before it becomes upload-ready. The current local
folder already includes production vendor dependencies.

Root `.htaccess` is essential: it maps public asset URLs and denies direct access
to private Laravel code. Keep the subdomain at `/`; do not add `/public` to its
browser URL. SSL and secure session cookies stay enabled in production.

## Shop details

**New Star Tailor** · Old UCO Bank Gully, Near Patel Plaza, Tagore Marg, Neemuch,
Madhya Pradesh · **+91 94240 35393**. Map coordinates: `24.4570252, 74.870045`.

The red/black star logo follows the real shop signboard. Product and shop images
already belong to this project; preserve the existing identity when updating it.
