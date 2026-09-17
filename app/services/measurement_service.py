"""Measurement versioning business logic.

Every save creates a new immutable ``MeasurementVersion`` and repoints the
customer's ``current_version_id`` at it. Nothing here ever edits an existing
version in place — that is what keeps old orders' measurements intact.
"""
from __future__ import annotations

from ..extensions import db
from ..models.audit_log import AuditLog
from ..models.customer import Customer
from ..models.measurement import Measurement, MeasurementVersion


def add_version(customer: Customer, data: dict, *, actor_id: int | None) -> MeasurementVersion:
    measurement = customer.measurement
    if measurement is None:
        measurement = Measurement(customer=customer)
        db.session.add(measurement)
        db.session.flush()

    existing = (
        MeasurementVersion.query.filter_by(measurement_id=measurement.id)
        .order_by(MeasurementVersion.version_number.desc())
        .first()
    )
    next_number = (existing.version_number + 1) if existing else 1

    version = MeasurementVersion(
        measurement_id=measurement.id,
        version_number=next_number,
        unit="in",
        **data,
    )
    db.session.add(version)
    db.session.flush()

    measurement.current_version_id = version.id
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="measurement",
            entity_id=version.id,
            action="create_version",
            to_value=f"customer={customer.id} version={next_number}",
        )
    )
    db.session.commit()
    return version
