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

## Notes
- `utf8mb4` is required for Hindi (Devanagari) text.
- Until Phase 2 there are no tables; `nst check` only tests connectivity.
- The test suite falls back to in-memory SQLite when `TEST_DATABASE_URL` is
  unset, but from Phase 2 you should set it so tests run on the real engine.
