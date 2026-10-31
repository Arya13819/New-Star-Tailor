# MySQL database delivery

`new_star_tailor.sql` is a fresh, empty application database with the real service
catalogue and Alembic revision `2e3b1bebff15`. It includes login accounts,
customers, versioned measurements, orders, order items, payments, order numbering,
reference-image metadata, enquiries, notifications, settings and audit logs.
No customer records, login passwords or sample orders are included.

**Choose one setup path:** migrations (recommended) OR the SQL import.
Do not import over existing tables. Back up an existing installation first.

## Option A: migrations

Create an empty `new_star_tailor` database using `utf8mb4_unicode_ci` and a dedicated
application user, then configure `.env` (see `docs/DATABASE_SETUP.md`). Run:

```sh
.venv/bin/flask --app wsgi db upgrade
.venv/bin/flask --app wsgi nst seed-services
```

## Option B: SQL import (including phpMyAdmin)

Create/select an empty `new_star_tailor` database, then import
`database/new_star_tailor.sql` in phpMyAdmin, or run:

```sh
mysql -h 127.0.0.1 -u nst_user -p new_star_tailor < database/new_star_tailor.sql
```

The file is schema plus catalogue; it is not a backup of anyone's orders. It
includes the migration revision, so subsequent `flask db upgrade` can apply future
changes normally. Never import it into a live database with existing tables.

## Configure and create your login

```ini
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://nst_user:URL_ENCODED_PASSWORD@127.0.0.1:3306/new_star_tailor?charset=utf8mb4
```

Generate a unique `SECRET_KEY`, then run:

```sh
.venv/bin/flask --app wsgi nst check
.venv/bin/flask --app wsgi nst create-admin
.venv/bin/flask --app wsgi run
```

`create-admin` prompts for the staff name, email, mobile and a private password.
No shared default admin account exists. Staff sign in at `/admin/login`;
customers register at `/customer/register` and sign in at `/customer/login`.
Staff manage orders and update status at `/admin/orders`. Customers view only their
own orders under `/customer/orders`; public tracking at `/track-order` requires
both the order number and matching mobile number.

## Optional local MySQL using Docker

Set `MYSQL_PASSWORD` and `MYSQL_ROOT_PASSWORD` in `.env`, then:

```sh
docker compose up -d mysql
docker compose ps
```

Wait for the database to be healthy. Set `DATABASE_URL` to the dedicated
`nst_user`, the same password, host `127.0.0.1`, port `3307` and database
`new_star_tailor`. Then use option A above. The database uses the persistent
`nst_mysql` volume. Do not delete the volume if it contains data you need.
This Compose file runs the database only; run Flask using the project virtualenv.

For production, configure HTTPS, `FLASK_ENV=production`, a unique `SECRET_KEY`,
regular database/upload backups and a private MySQL host. `render.yaml` remains
the original PostgreSQL deployment option; it does not provision MySQL.
