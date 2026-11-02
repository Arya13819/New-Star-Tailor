# New Star Tailor — Laravel + MySQL

Ek hi working/upload folder:
`/home/shyam/Documents/Work/newstartailor`

PHP target: **8.3.36**. Laravel 13; frontend ke liye Node/Vite build nahi chahiye.

## Code kahan milega?

| Kaam | File/folder |
| --- | --- |
| URL se controller mapping | `routes/web.php` |
| Home, About, Contact, Services, tracking | `app/Http/Controllers/PublicController.php` |
| Login, signup, first admin setup | `app/Http/Controllers/AuthController.php` |
| New order, order details, photos, receipts | `app/Http/Controllers/OrderController.php` |
| Customer account screens | `app/Http/Controllers/CustomerController.php` |
| Staff management and reports | `app/Http/Controllers/AdminController.php` |
| Shared session/error handling | `app/Http/Controllers/TailoringController.php` |
| Order/payment calculations and validation | `app/Tailoring/services.php` |
| Shared formatting/database/view helpers | `app/Tailoring/bootstrap.php` |
| Shared request guards and system endpoints | `app/Tailoring/controllers.php` |
| Header, footer, navigation | `resources/views/layouts/app.blade.php` |
| Home/About/Contact HTML | `resources/views/pages/marketing/en/` and `hi/` |
| Services catalogue HTML | `resources/views/pages/services.blade.php` |
| Login/signup HTML | `resources/views/pages/auth.blade.php` |
| Order form HTML | `resources/views/pages/order_form.blade.php` |
| Other management HTML | `resources/views/pages/*.blade.php` |
| CSS, JavaScript, photos, logo | `public/static/`, `public/assets/` |
| MySQL credentials | `.env` (private; not committed) |

Views use Blade loops, conditions, includes and escaped output. Existing monetary
precision, payment verification and customer isolation rules are preserved.

## FileZilla upload

Read [FILEZILLA_SETUP_HINDI.md](FILEZILLA_SETUP_HINDI.md).
Upload **the contents of this folder** into
`/domains/itgurujan.com/public_html/newstartailor/`.
The root `index.php` loads `public/index.php`; `.htaccess` maps public assets and blocks private Laravel files.
No extra `newstartailor-app` folder is used. Do not move view files into `public/`.

The database is already imported: **do not reimport SQL or run migrate:fresh**.
Runtime dependencies are included in `vendor/` for upload; no server Composer step
is needed. On later code-only updates preserve `.env` and `storage/`.

## Local development

Use PHP >=8.3 with Laravel's standard extensions and PDO MySQL.
Run `composer install` to install developer tools. Use a separate local `.env`
with local MySQL credentials and `SESSION_SECURE_COOKIE=false`, then
`php artisan serve`. Do not use live database credentials for development tests.
The supplied `.env` is configured for hosting; keep it private.

Run `php artisan test` and `vendor/bin/pint --dirty --format agent`.
`tests/http_edge_cases.py` is the real HTTP/MySQL suite; it only permits a guarded
local `_test` database and URL. `NST_TEST_ENV` can select a separate QA env file.
Before uploading, `composer install --no-dev --optimize-autoloader` keeps vendor
free of developer tools. Production dependencies target PHP 8.3.36 in composer.lock.
