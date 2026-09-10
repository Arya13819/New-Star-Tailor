# Backups (outline — finalised at Phase 18)

Customer, order and payment data is business-critical. Losing it is losing the
shop's diary.

## What to back up
1. **Database** — everything.
2. **`instance/uploads/`** — reference images (not in the database).
3. **`.env`** — store the production secrets somewhere safe and separate.

## Database — daily dump
```bash
mysqldump --single-transaction --routines --triggers \
  -u nst_user -p nst_prod | gzip > /var/backups/nst/nst_$(date +%F).sql.gz
```
- Run via cron, e.g. 02:00 daily.
- Keep 14 daily + 8 weekly copies (adjust to taste).
- Copy off-server (rsync / object storage) — a backup on the same disk is not a backup.

## Uploads
```bash
rsync -a --delete instance/uploads/ /var/backups/nst/uploads/
```

## Restore test
Every month, restore the latest dump into a scratch database and boot the app
against it. An untested backup is a hope, not a backup.

## Retention
Payment and order records: keep indefinitely (business/tax records).
