"""Enumerations used across the data model.

Stored as short strings (``native_enum=False``) so they behave identically on
MySQL/MariaDB and SQLite and are trivial to extend without a schema migration
to an ``ENUM`` type.
"""
from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


class ServiceCategory(StrEnum):
    SHIRT = "SHIRT"
    PANT = "PANT"
    POLICE = "POLICE"
    CRPF = "CRPF"
    ARMY = "ARMY"


class FittingPreference(StrEnum):
    LOOSE = "LOOSE"
    NORMAL = "NORMAL"
    SLIM = "SLIM"


class MeasurementSource(StrEnum):
    SHOP = "SHOP"
    CUSTOMER = "CUSTOMER"


class OrderSource(StrEnum):
    SHOP = "SHOP"
    WEBSITE = "WEBSITE"


class OrderStatus(StrEnum):
    NEW = "NEW"
    MEASUREMENT = "MEASUREMENT"
    READY = "READY"
    DELIVERED = "DELIVERED"


class OrderPriority(StrEnum):
    NORMAL = "NORMAL"
    URGENT = "URGENT"


class FabricSource(StrEnum):
    CUSTOMER = "CUSTOMER"
    SHOP = "SHOP"


class PaymentMethod(StrEnum):
    CASH = "CASH"
    UPI = "UPI"
    ONLINE = "ONLINE"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class NotificationChannel(StrEnum):
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    EMAIL = "EMAIL"


class NotificationType(StrEnum):
    ORDER_CONFIRMATION = "ORDER_CONFIRMATION"
    ORDER_READY = "ORDER_READY"
    DELIVERY_REMINDER = "DELIVERY_REMINDER"
    PAYMENT_REMINDER = "PAYMENT_REMINDER"


class NotificationStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class EnquiryStatus(StrEnum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    CLOSED = "CLOSED"
