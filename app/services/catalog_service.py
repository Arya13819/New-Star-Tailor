"""Service catalogue business logic.

Prices live here, not hard-coded in templates or order logic (master prompt
§6). A service with no price yet is a normal, expected state — the owner
said several rates would come "later" — it is simply not usable on an order
until priced (enforced when order creation is built in Phase 7).
"""
from __future__ import annotations

from decimal import Decimal

from ..extensions import db
from ..models.audit_log import AuditLog
from ..models.enums import ServiceCategory
from ..models.service import Service

# Known prices at rewrite time (master prompt §4). Anything not listed here
# is seeded with no price and must be set from /admin/services before it can
# be used on an order.
DEFAULT_SERVICES: list[dict] = [
    {"code": "SHIRT", "name_en": "Shirt", "name_hi": "शर्ट",
     "category": ServiceCategory.SHIRT, "price": None, "sort_order": 10},
    {"code": "PANT", "name_en": "Pant", "name_hi": "पैंट",
     "category": ServiceCategory.PANT, "price": None, "sort_order": 20},
    {"code": "SHIRT_PANT_COMBO", "name_en": "Shirt + Pant Combo", "name_hi": "शर्ट + पैंट सेट",
     "category": ServiceCategory.SHIRT, "price": Decimal("550.00"), "sort_order": 30},
    {"code": "POLICE_KHAAKI", "name_en": "Police Khaaki", "name_hi": "पुलिस खाकी",
     "category": ServiceCategory.POLICE, "price": Decimal("700.00"), "sort_order": 40},
    {"code": "CRPF_KHAAKI", "name_en": "CRPF Khaaki", "name_hi": "सीआरपीएफ खाकी",
     "category": ServiceCategory.CRPF, "price": Decimal("700.00"), "sort_order": 50},
    {"code": "CRPF_CHEETAH", "name_en": "CRPF Cheetah", "name_hi": "सीआरपीएफ चीता",
     "category": ServiceCategory.CRPF, "price": Decimal("700.00"), "sort_order": 60},
    {"code": "CRPF_KHAAKI_DANGRI", "name_en": "CRPF Khaaki Dangri", "name_hi": "सीआरपीएफ खाकी डंगरी",
     "category": ServiceCategory.CRPF, "price": None, "sort_order": 70},
    {"code": "ARMY_PATTERN", "name_en": "Army Pattern", "name_hi": "आर्मी पैटर्न",
     "category": ServiceCategory.ARMY, "price": None, "sort_order": 80},
    {"code": "CHEETAH_US_PATTERN", "name_en": "Cheetah US Pattern", "name_hi": "चीता यूएस पैटर्न",
     "category": ServiceCategory.ARMY, "price": Decimal("850.00"), "sort_order": 90},
]


def seed_defaults(*, actor_id: int | None = None) -> int:
    """Insert any DEFAULT_SERVICES not already present, by code. Idempotent —
    never touches a service that already exists (so a manually-edited price
    is never overwritten by re-seeding)."""
    existing_codes = {c for (c,) in db.session.query(Service.code).all()}
    created = 0
    for spec in DEFAULT_SERVICES:
        if spec["code"] in existing_codes:
            continue
        service = Service(
            code=spec["code"],
            name_en=spec["name_en"],
            name_hi=spec["name_hi"],
            category=spec["category"],
            default_stitching_price=spec["price"],
            sort_order=spec["sort_order"],
            is_active=True,
        )
        db.session.add(service)
        db.session.flush()
        db.session.add(
            AuditLog(
                actor_user_id=actor_id,
                entity_type="service",
                entity_id=service.id,
                action="seed",
                to_value=service.code,
            )
        )
        created += 1
    db.session.commit()
    return created


def create_service(*, actor_id: int | None, **fields) -> Service:
    service = Service(**fields)
    db.session.add(service)
    db.session.flush()
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="service",
            entity_id=service.id,
            action="create",
            to_value=service.code,
        )
    )
    db.session.commit()
    return service


def update_service(service: Service, *, actor_id: int | None, **fields) -> Service:
    before_price = service.default_stitching_price
    for key, value in fields.items():
        setattr(service, key, value)
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="service",
            entity_id=service.id,
            action="update",
            from_value=f"price={before_price}",
            to_value=f"price={service.default_stitching_price}",
        )
    )
    db.session.commit()
    return service


def toggle_active(service: Service, *, actor_id: int | None) -> Service:
    service.is_active = not service.is_active
    db.session.add(
        AuditLog(
            actor_user_id=actor_id,
            entity_type="service",
            entity_id=service.id,
            action="toggle_active",
            to_value=str(service.is_active),
        )
    )
    db.session.commit()
    return service
