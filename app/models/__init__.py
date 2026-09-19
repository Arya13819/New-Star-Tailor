"""SQLAlchemy models.

Importing this package registers every model on the shared ``db.metadata`` so
Flask-Migrate autogenerate sees them.
"""
from __future__ import annotations

from ..extensions import db
from .audit_log import AuditLog
from .customer import Customer
from .enquiry import Enquiry
from .measurement import Measurement, MeasurementVersion
from .notification import Notification
from .order import Order, OrderItem, OrderSequence
from .payment import Payment, PaymentEvent
from .reference_image import ReferenceImage
from .service import Service
from .setting import Setting
from .user import User

__all__ = [
    "db",
    "AuditLog",
    "Customer",
    "Enquiry",
    "Measurement",
    "MeasurementVersion",
    "Notification",
    "Order",
    "OrderItem",
    "OrderSequence",
    "Payment",
    "PaymentEvent",
    "ReferenceImage",
    "Service",
    "Setting",
    "User",
]
