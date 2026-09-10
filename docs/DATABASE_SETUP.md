# Database setup (MySQL / MariaDB)

The app targets **MySQL 8**. **MariaDB 10.6+ / 11.x** is a supported drop-in
(the SQLAlchemy `mysql+pymysql` driver treats them the same for everything this
app uses). This machine already runs **MariaDB 11.8** on `127.0.0.1:3306`.

## 1. Create the database and user

You need an account that can create databases (root, or `sudo mysql` on a
default Debian/Ubuntu MariaDB install). Run:

```sql
-- as root / via: sudo mysql
CREATE DATABASE nst_dev  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE nst_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'nst_user'@'localhost' IDENTIFIED BY 'choose-a-password';
GRANT ALL PRIVILEGES ON nst_dev.*  TO 'nst_user'@'localhost';
GRANT ALL PRIVILEGES ON nst_test.* TO 'nst_user'@'localhost';
FLUSH PRIVILEGES;
```

One-liner form:

```bash
sudo mysql <<'SQL'
CREATE DATABASE IF NOT EXISTS nst_dev  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS nst_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'nst_user'@'localhost' IDENTIFIED BY 'choose-a-password';
GRANT ALL PRIVILEGES ON nst_dev.*  TO 'nst_user'@'localhost';
GRANT ALL PRIVILEGES ON nst_test.* TO 'nst_user'@'localhost';
FLUSH PRIVILEGES;
SQL
```

## 2. Point the app at it

In `.env`:

```
DATABASE_URL=mysql+pymysql://nst_user:choose-a-password@127.0.0.1:3306/nst_dev?charset=utf8mb4
TEST_DATABASE_URL=mysql+pymysql://nst_user:choose-a-password@127.0.0.1:3306/nst_test?charset=utf8mb4
```

## 3. Verify

```bash
.venv/bin/flask --app wsgi nst check
```

Expect `Database : reachable`. Migrations (`flask db upgrade`) arrive in Phase 2.

## Running without MySQL (temporary)

If `DATABASE_URL` is blank the app uses a local SQLite file
(`instance/nst_dev.sqlite`) and the test suite uses in-memory SQLite. The
models are written MySQL-first, so switching later is just a matter of setting
`DATABASE_URL` / `TEST_DATABASE_URL` and running `flask db upgrade`.

## Applying the schema

```bash
.venv/bin/flask --app wsgi db upgrade     # runs all migrations
.venv/bin/flask --app wsgi nst check      # shows "Schema revision : <id>"
```

## Notes
- `utf8mb4` is required for Hindi (Devanagari) text.
- Prefer setting `TEST_DATABASE_URL` to `nst_test` on MySQL so tests run on the
  real engine before release.
