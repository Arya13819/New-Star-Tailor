"""Key/value application settings (shop info, prices policy, reminder policy…).

Values are JSON-encoded text so a setting can hold a string, number or object.
"""
from __future__ import annotations

import json
from datetime import datetime

from .base import TABLE_ARGS, Mapped, PkMixin, db, mapped_column, sa, utcnow


class Setting(PkMixin, db.Model):
    __tablename__ = "settings"
    __table_args__ = TABLE_ARGS

    key: Mapped[str] = mapped_column(sa.String(120), nullable=False, unique=True)
    value_json: Mapped[str | None] = mapped_column(sa.Text)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    @property
    def value(self):
        if self.value_json is None:
            return None
        try:
            return json.loads(self.value_json)
        except (ValueError, TypeError):
            return self.value_json

    @value.setter
    def value(self, obj) -> None:
        self.value_json = json.dumps(obj, ensure_ascii=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Setting {self.key}>"
