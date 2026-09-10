"""WSGI entrypoint.

Local:  flask --app wsgi run
Prod:   gunicorn "wsgi:app" -c gunicorn.conf.py
"""
from __future__ import annotations

import os

from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))
