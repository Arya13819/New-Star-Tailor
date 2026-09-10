"""Measurements and their immutable version history.

A ``Measurement`` is the per-customer container. Each edit creates a new
``MeasurementVersion``; ``current_version_id`` points at the latest. Orders
reference the exact version used, so editing measurements never changes an
old order.
"""
from __future__ import annotations

from datetime import datetime

from .base import TABLE_ARGS, Mapped, PkMixin, TimestampMixin, db, mapped_column, sa, utcnow
from .enums import FittingPreference, MeasurementSource

# Numeric spec for a measurement value in inches (e.g. 42.50, 16.25).
_INCHES = sa.Numeric(5, 2, asdecimal=True)


class Measurement(PkMixin, TimestampMixin, db.Model):
    __tablename__ = "measurements"
    __table_args__ = TABLE_ARGS

    customer_id: Mapped[int] = mapped_column(
        sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # Plain column, not a DB foreign key: measurements <-> measurement_versions
    # are mutually referential, and this pointer is always set by the
    # measurement service to a version it just created. Avoiding the FK keeps
    # the schema free of a circular constraint.
    current_version_id: Mapped[int | None] = mapped_column(sa.Integer, index=True)

    customer = db.relationship("Customer", back_populates="measurement")
    current_version = db.relationship(
        "MeasurementVersion",
        primaryjoin="foreign(Measurement.current_version_id) == MeasurementVersion.id",
        uselist=False,
        post_update=True,
    )
    versions = db.relationship(
        "MeasurementVersion",
        back_populates="measurement",
        primaryjoin="Measurement.id == MeasurementVersion.measurement_id",
        order_by="MeasurementVersion.version_number",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Measurement customer={self.customer_id} current={self.current_version_id}>"


class MeasurementVersion(PkMixin, db.Model):
    __tablename__ = "measurement_versions"
    __table_args__ = (
        sa.UniqueConstraint("measurement_id", "version_number", name="uq_measurement_version"),
        TABLE_ARGS,
    )

    measurement_id: Mapped[int] = mapped_column(
        sa.ForeignKey("measurements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    # Shirt (inches)
    shirt_length: Mapped[float | None] = mapped_column(_INCHES)
    shirt_chest: Mapped[float | None] = mapped_column(_INCHES)
    shirt_shoulder: Mapped[float | None] = mapped_column(_INCHES)
    shirt_sleeves: Mapped[float | None] = mapped_column(_INCHES)
    shirt_neck: Mapped[float | None] = mapped_column(_INCHES)

    # Pant (inches)
    pant_length: Mapped[float | None] = mapped_column(_INCHES)
    pant_waist: Mapped[float | None] = mapped_column(_INCHES)
    pant_hips: Mapped[float | None] = mapped_column(_INCHES)
    pant_mori: Mapped[float | None] = mapped_column(_INCHES)

    unit: Mapped[str] = mapped_column(sa.String(4), nullable=False, default="in")
    fitting_preference: Mapped[FittingPreference | None] = mapped_column(
        sa.Enum(FittingPreference, native_enum=False, length=10)
    )
    allowance: Mapped[str | None] = mapped_column(sa.String(120))
    notes: Mapped[str | None] = mapped_column(sa.Text)
    alteration_notes: Mapped[str | None] = mapped_column(sa.Text)

    source: Mapped[MeasurementSource] = mapped_column(
        sa.Enum(MeasurementSource, native_enum=False, length=10),
        nullable=False,
        default=MeasurementSource.SHOP,
    )
    created_by_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=utcnow
    )

    measurement = db.relationship(
        "Measurement",
        back_populates="versions",
        foreign_keys=[measurement_id],
    )
    created_by = db.relationship("User")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MeasurementVersion m={self.measurement_id} v{self.version_number}>"
