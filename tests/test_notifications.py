"""Phase 13: WhatsApp-ready notification architecture."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from app.models.customer import Customer
from app.models.enums import (
    FabricSource,
    NotificationStatus,
    NotificationType,
    OrderPriority,
    OrderStatus,
    PaymentMethod,
    ServiceCategory,
    UserRole,
)
from app.models.notification import Notification
from app.models.service import Service
from app.models.user import User
from app.services.notification_service import (
    dispatch_pending,
    queue_notification,
    queue_payment_reminders,
)
from app.services.order_service import create_order, update_status
from app.services.payment_service import record_payment


def _login_admin(client, db):
    u = User(name="Owner", email="owner@example.com", role=UserRole.ADMIN)
    u.set_password("supersecret1")
    db.session.add(u)
    db.session.commit()
    client.post("/admin/login", data={"identifier": "owner@example.com", "password": "supersecret1"})
    return u


def _order(db, price="550.00"):
    c = Customer(name="Ramesh", mobile="9000000010")
    db.session.add(c)
    db.session.commit()
    s = Service(code="SVC", name_en="Service", category=ServiceCategory.SHIRT,
                default_stitching_price=Decimal(price))
    db.session.add(s)
    db.session.commit()
    return create_order(
        customer=c,
        items=[{"service_id": s.id, "service_name": s.name_en, "category": s.category,
                 "quantity": 1, "stitching_price": Decimal(price)}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )


# --- queueing hooks --------------------------------------------------------


def test_creating_an_order_queues_a_confirmation(app, db):
    order = _order(db)
    note = Notification.query.filter_by(order_id=order.id).one()
    assert note.type == NotificationType.ORDER_CONFIRMATION
    assert note.status == NotificationStatus.SCHEDULED
    assert note.to_address == order.customer.mobile


def test_marking_ready_twice_in_a_row_does_not_duplicate(app, db):
    order = _order(db)
    update_status(order, OrderStatus.READY, actor_id=None)
    update_status(order, OrderStatus.READY, actor_id=None)  # already READY - no-op

    ready_notes = Notification.query.filter_by(
        order_id=order.id, type=NotificationType.ORDER_READY
    ).all()
    assert len(ready_notes) == 1


def test_re_readying_after_a_revert_notifies_again(app, db):
    order = _order(db)
    update_status(order, OrderStatus.READY, actor_id=None)
    update_status(order, OrderStatus.NEW, actor_id=None)
    update_status(order, OrderStatus.READY, actor_id=None)  # a genuine new transition

    ready_notes = Notification.query.filter_by(
        order_id=order.id, type=NotificationType.ORDER_READY
    ).all()
    assert len(ready_notes) == 2


# --- dispatch honesty --------------------------------------------------


def test_dispatch_pending_without_provider_touches_nothing(app, db):
    order = _order(db)
    before = Notification.query.filter_by(order_id=order.id).one()
    assert before.status == NotificationStatus.SCHEDULED

    result = dispatch_pending()
    assert result["configured"] is False
    assert result["pending"] >= 1

    db.session.refresh(before)
    assert before.status == NotificationStatus.SCHEDULED  # untouched, never faked


def test_queue_notification_dedupe_key_prevents_duplicates(app, db):
    c = Customer(name="Ramesh", mobile="9000000010")
    db.session.add(c)
    db.session.commit()

    first = queue_notification(
        customer=c, type_="PAYMENT_REMINDER", body="test", dedupe_key="dup-key-1"
    )
    second = queue_notification(
        customer=c, type_="PAYMENT_REMINDER", body="test again", dedupe_key="dup-key-1"
    )
    assert first is not None
    assert second is None
    assert Notification.query.filter_by(dedupe_key="dup-key-1").count() == 1


# --- payment reminders ---------------------------------------------------


def test_payment_reminder_queued_for_overdue_unpaid_delivered_order(app, db):
    order = _order(db)
    update_status(order, OrderStatus.DELIVERED, actor_id=None)
    order.delivered_at = order.delivered_at - timedelta(days=8)
    db.session.commit()

    count = queue_payment_reminders()
    assert count == 1
    reminder = Notification.query.filter_by(
        order_id=order.id, type=NotificationType.PAYMENT_REMINDER
    ).one()
    assert reminder.status == NotificationStatus.SCHEDULED


def test_no_reminder_when_fully_paid(app, db):
    order = _order(db)
    record_payment(order=order, amount=Decimal("550"), method=PaymentMethod.CASH,
                    transaction_reference=None, note=None, actor_id=None)
    update_status(order, OrderStatus.DELIVERED, actor_id=None)
    order.delivered_at = order.delivered_at - timedelta(days=8)
    db.session.commit()

    count = queue_payment_reminders()
    assert count == 0


def test_no_reminder_before_the_grace_period(app, db):
    order = _order(db)
    update_status(order, OrderStatus.DELIVERED, actor_id=None)
    order.delivered_at = order.delivered_at - timedelta(days=2)
    db.session.commit()

    count = queue_payment_reminders()
    assert count == 0


def test_reminder_not_duplicated_same_day(app, db):
    order = _order(db)
    update_status(order, OrderStatus.DELIVERED, actor_id=None)
    order.delivered_at = order.delivered_at - timedelta(days=10)
    db.session.commit()

    first = queue_payment_reminders()
    second = queue_payment_reminders()
    assert first == 1
    assert second == 0  # already queued today


# --- admin visibility ----------------------------------------------------


def test_admin_can_view_notifications(client, db):
    _login_admin(client, db)
    _order(db)
    resp = client.get("/admin/notifications")
    assert resp.status_code == 200
    assert b"Order Confirmation" in resp.data


def test_admin_notifications_requires_admin(client):
    resp = client.get("/admin/notifications")
    assert resp.status_code == 302


def test_cli_notifications_process(app, db):
    _order(db)
    runner = app.test_cli_runner()
    result = runner.invoke(args=["nst", "notifications", "process"])
    assert result.exit_code == 0
    assert "not configured" in result.output.lower()


def test_cli_reminders_run(app, db):
    order = _order(db)
    update_status(order, OrderStatus.DELIVERED, actor_id=None)
    order.delivered_at = order.delivered_at - timedelta(days=10)
    db.session.commit()

    runner = app.test_cli_runner()
    result = runner.invoke(args=["nst", "reminders", "run"])
    assert result.exit_code == 0
    assert "Queued 1" in result.output
