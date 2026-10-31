# Database setup (MySQL / MariaDB)

The app targets **MySQL 8**. **MariaDB 10.6+ / 11.x** is a supported drop-in
(the SQLAlchemy `mysql+pymysql` driver treats them the same for everything this
app uses). This machine runs **MariaDB 11.8** on `127.0.0.1:3306`, and as of
2026-09-18 the app is provisioned against it (`nst_dev` / `nst_test`,
credentials in the local `.env`, not committed).

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

## Troubleshooting: `sudo mysql` says "Access denied for user 'root'@'localhost'"

On some installs (this machine included) MariaDB's `root` account has a real
password set instead of the usual `unix_socket`/`auth_socket` plugin, so
`sudo mysql` does **not** auto-authenticate. `sudo mysql --defaults-file=/etc/mysql/debian.cnf`
(the Debian maintenance account) may also fail if that account was removed.

Fix used here — reset access without knowing the old root password, without
touching root's password permanently:

```bash
sudo systemctl stop mariadb
sudo mkdir -p /run/mysqld && sudo chown mysql:mysql /run/mysqld   # recreated each stop
# Run AS the mysql user directly — avoids the setuid/setgid AppArmor denies
# you get from `sudo mysqld_safe ...` (mariadbd can't drop root->mysql under
# the default AppArmor profile when started that way):
sudo -u mysql /usr/sbin/mariadbd --skip-grant-tables --skip-networking &
sleep 5
sudo mysql -e "SELECT 1;"   # should succeed with no auth
# ... run your CREATE DATABASE / CREATE USER / GRANT statements here ...
sudo pkill -9 mariadbd      # `mysqladmin shutdown` also hit the access-denied
sleep 3
sudo systemctl start mariadb
sudo systemctl status mariadb --no-pager   # expect active (running)
```

A stray still-running `--skip-grant-tables` instance colliding with a fresh
`systemctl start` produces `Plugin 'InnoDB' registration ... failed` /
`Unknown storage engine 'Aria'` — harmless (InnoDB crash-recovers on the next
clean start), but always confirm `pgrep -a mariadbd` is empty before starting
the service again.
