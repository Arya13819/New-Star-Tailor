
-- PHP-only security and idempotency tables. Add to an existing Flask schema
-- with database/php_extensions.sql; never re-import the full schema over data.
CREATE TABLE IF NOT EXISTS php_rate_limits (
 bucket CHAR(64) NOT NULL PRIMARY KEY,
 window_start BIGINT UNSIGNED NOT NULL,
 attempts INT UNSIGNED NOT NULL,
 INDEX ix_php_rate_window (window_start)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE IF NOT EXISTS php_submissions (
 token CHAR(64) NOT NULL PRIMARY KEY,
 order_id INT DEFAULT NULL,
 created_at DATETIME NOT NULL,
 INDEX ix_php_submission_order (order_id),
 CONSTRAINT fk_php_submission_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add this only if users.remember_token does not exist.
ALTER TABLE users ADD COLUMN remember_token VARCHAR(100) NULL;
