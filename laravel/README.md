# New Star Tailor — Laravel

Laravel 13 + MySQL application for Hostinger PHP 8.3.36 shared hosting.
The original Flask project remains one directory above; this is the production
PHP application. It uses Laravel authentication, sessions, CSRF protection,
routes, middleware and PHP views with transactional tailoring business logic.

## Upload using FileZilla

Read [FILEZILLA_SETUP_HINDI.md](FILEZILLA_SETUP_HINDI.md). The release archive
includes `vendor/`; no SSH, Composer or Node build is needed on Hostinger.
Public files and private application files must use the separate locations
shown in that guide. MySQL credentials belong only in the private `.env`.

## Local development

Use PHP >=8.3 with PDO MySQL, mbstring, XML, curl, fileinfo and the standard
Laravel extensions. Run `composer install`, copy `.env.example` to `.env`,
configure an empty local MySQL database, run `php artisan key:generate`,
`php artisan migrate`, set `NST_SETUP_KEY` to a private random value, then run
`php artisan serve`. Open `/setup` to create the first administrator.
No default customer or administrator account is created.

Frontend CSS/JS/images require no Vite build. Shared static source lives in
`../app/static`; the archive builder copies it into `public/static`.
Laravel-specific assets live in `public/assets`.

## Verification and release

Run `php artisan test` and `vendor/bin/pint --dirty --format agent`.
The real HTTP/MySQL integration tests under `tests/http_*.py` deliberately
require an isolated `_test` database and a local QA server; never run them
against production. Read their environment guards before use.

Before packaging, run `composer install --no-dev --optimize-autoloader` here,
then `python3 scripts/build_laravel_hostinger.py` from the repository root.
The builder rejects development vendor installations and generates fresh
private encryption/setup keys in the archive only. Keep that ZIP private.
