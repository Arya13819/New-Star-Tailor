"""Phase 11: public enquiry, online ordering, and order tracking."""
from __future__ import annotations

from decimal import Decimal

from app.models.enquiry import Enquiry
from app.models.enums import EnquiryStatus, OrderSource, PaymentStatus, ServiceCategory, UserRole
from app.models.order import Order
from app.models.payment import Payment
from app.models.service import Service
from app.models.user import User


def _service(db, price="550.00"):
    s = Service(code="SHIRT_PANT_COMBO", name_en="Shirt + Pant Combo",
                category=ServiceCategory.SHIRT, default_stitching_price=Decimal(price))
    db.session.add(s)
    db.session.commit()
    return s


def _login_admin(client, db):
    u = User(name="Owner", email="owner@example.com", role=UserRole.ADMIN)
    u.set_password("supersecret1")
    db.session.add(u)
    db.session.commit()
    client.post("/admin/login", data={"identifier": "owner@example.com", "password": "supersecret1"})
    return u


# --- Enquiry -----------------------------------------------------------


def test_enquiry_page_renders(client):
    resp = client.get("/enquiry")
    assert resp.status_code == 200


def test_submit_enquiry_creates_record(client, db):
    resp = client.post(
        "/enquiry",
        data={"name": "Test Enquirer", "mobile": "9444444444", "message": "need 2 shirts"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    enq = Enquiry.query.filter_by(mobile="9444444444").one()
    assert enq.name == "Test Enquirer"
    assert enq.status == EnquiryStatus.NEW


def test_admin_can_see_and_update_enquiry(client, db):
    _login_admin(client, db)
    client.post("/enquiry", data={"name": "Test Enquirer", "mobile": "9444444444"})
    enq = Enquiry.query.filter_by(mobile="9444444444").one()

    resp = client.get("/admin/enquiries")
    assert b"Test Enquirer" in resp.data

    client.post(f"/admin/enquiries/{enq.id}/status", data={"status": "CONTACTED"})
    db.session.refresh(enq)
    assert enq.status == EnquiryStatus.CONTACTED


def test_admin_enquiries_requires_admin(client):
    assert client.get("/admin/enquiries").status_code == 302


def test_new_enquiry_alerts_the_shop_number(client, db):
    from app.config import Config
    from app.models.enums import NotificationType
    from app.models.notification import Notification

    client.post(
        "/enquiry",
        data={"name": "Test Enquirer", "mobile": "9444444444", "message": "need 2 shirts"},
    )
    alert = Notification.query.filter_by(type=NotificationType.NEW_ENQUIRY).one()
    assert alert.customer_id is None
    assert alert.to_address == Config.SHOP_PHONE
    assert "Test Enquirer" in alert.body
    assert "need 2 shirts" in alert.body


# --- Enquiry -> order conversion ----------------------------------------


def test_convert_creates_a_new_customer_and_redirects_to_order_form(client, db):
    _login_admin(client, db)
    client.post("/enquiry", data={"name": "Ramesh", "mobile": "9444444444", "message": "2 shirts"})
    enq = Enquiry.query.filter_by(mobile="9444444444").one()

    resp = client.post(f"/admin/enquiries/{enq.id}/convert")
    assert resp.status_code == 302
    assert "/admin/orders/new?customer_id=" in resp.headers["Location"]
    assert f"enquiry_id={enq.id}" in resp.headers["Location"]

    from app.models.customer import Customer

    customer = Customer.query.filter_by(mobile="9444444444").one()
    assert customer.name == "Ramesh"


def test_completing_the_order_marks_the_enquiry_converted(client, db):
    _login_admin(client, db)
    _service(db)
    client.post("/enquiry", data={"name": "Ramesh", "mobile": "9444444444"})
    enq = Enquiry.query.filter_by(mobile="9444444444").one()

    convert_resp = client.post(f"/admin/enquiries/{enq.id}/convert")
    location = convert_resp.headers["Location"]

    service = Service.query.filter_by(code="SHIRT_PANT_COMBO").one()
    resp = client.post(
        location,
        data={
            "items-0-service_id": str(service.id),
            "items-0-quantity": "1",
            "items-0-stitching_price": "550.00",
            "items-0-material_price": "0",
            "fabric_source": "CUSTOMER",
            "priority": "NORMAL",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302

    db.session.refresh(enq)
    assert enq.status == EnquiryStatus.CONVERTED
    assert enq.converted_order_id is not None

    order = db.session.get(Order, enq.converted_order_id)
    assert order.customer.mobile == "9444444444"


def test_converted_enquiry_shows_no_convert_button_and_links_the_order(client, db):
    _login_admin(client, db)
    _service(db)
    client.post("/enquiry", data={"name": "Ramesh", "mobile": "9444444444"})
    enq = Enquiry.query.filter_by(mobile="9444444444").one()
    convert_resp = client.post(f"/admin/enquiries/{enq.id}/convert")
    service = Service.query.filter_by(code="SHIRT_PANT_COMBO").one()
    client.post(
        convert_resp.headers["Location"],
        data={
            "items-0-service_id": str(service.id),
            "items-0-quantity": "1",
            "items-0-stitching_price": "550.00",
            "items-0-material_price": "0",
            "fabric_source": "CUSTOMER",
            "priority": "NORMAL",
        },
    )

    resp = client.get("/admin/enquiries")
    assert b"Converted" in resp.data
    assert b"Convert to order" not in resp.data


def test_re_converting_an_already_converted_enquiry_goes_to_its_order(client, db):
    _login_admin(client, db)
    _service(db)
    client.post("/enquiry", data={"name": "Ramesh", "mobile": "9444444444"})
    enq = Enquiry.query.filter_by(mobile="9444444444").one()
    convert_resp = client.post(f"/admin/enquiries/{enq.id}/convert")
    service = Service.query.filter_by(code="SHIRT_PANT_COMBO").one()
    client.post(
        convert_resp.headers["Location"],
        data={
            "items-0-service_id": str(service.id),
            "items-0-quantity": "1",
            "items-0-stitching_price": "550.00",
            "items-0-material_price": "0",
            "fabric_source": "CUSTOMER",
            "priority": "NORMAL",
        },
    )
    db.session.refresh(enq)

    resp = client.post(f"/admin/enquiries/{enq.id}/convert")
    assert resp.status_code == 302
    assert resp.headers["Location"] == f"/admin/orders/{enq.converted_order_id}"


def test_unconverted_enquiry_never_appears_in_the_orders_list(client, db):
    _login_admin(client, db)
    client.post("/enquiry", data={"name": "Ramesh", "mobile": "9444444444"})

    resp = client.get("/admin/orders")
    assert b"Ramesh" not in resp.data


# --- Complete online order -----------------------------------------------


def test_online_order_page_renders(client, db):
    _service(db)
    resp = client.get("/order")
    assert resp.status_code == 200


def test_online_order_unavailable_without_priced_services(client, db):
    resp = client.get("/order")
    assert b"temporarily unavailable" in resp.data


def test_complete_online_order_creates_order_with_website_source(client, db):
    s = _service(db)
    resp = client.post(
        "/order",
        data={
            "name": "Online Customer",
            "mobile": "9555555555",
            "address": "Some Street",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "fabric_source": "CUSTOMER",
            "notes": "please rush",
        },
    )
    assert resp.status_code == 200
    assert b"NST-0001" in resp.data

    order = Order.query.filter_by(order_number="NST-0001").one()
    assert order.source == OrderSource.WEBSITE
    assert order.grand_total == Decimal("550.00")
    assert order.self_measurement_acknowledged is False


def test_online_order_never_trusts_a_client_supplied_price(client, db):
    """The public form has no price field at all, but even if one were
    smuggled in, the server must use the service's own price."""
    s = _service(db, price="550.00")
    client.post(
        "/order",
        data={
            "name": "Attacker",
            "mobile": "9555555556",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "items-0-stitching_price": "1",  # not a real field, should be ignored
            "fabric_source": "CUSTOMER",
        },
    )
    order = Order.query.filter_by(order_number="NST-0001").one()
    assert order.grand_total == Decimal("550.00")  # not 1.00


def test_online_order_with_self_measurements_requires_acknowledgement(client, db):
    s = _service(db)
    resp = client.post(
        "/order",
        data={
            "name": "Online Customer",
            "mobile": "9555555555",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "fabric_source": "CUSTOMER",
            "provide_measurements": "y",
            "shirt_chest": "40",
            # measurement_ack intentionally omitted
        },
    )
    assert Order.query.count() == 0  # rejected
    assert resp.status_code == 200


def test_online_order_with_acknowledged_self_measurements(client, db):
    s = _service(db)
    client.post(
        "/order",
        data={
            "name": "Online Customer",
            "mobile": "9555555555",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "fabric_source": "CUSTOMER",
            "provide_measurements": "y",
            "shirt_chest": "40",
            "measurement_ack": "y",
        },
    )
    order = Order.query.filter_by(order_number="NST-0001").one()
    assert order.self_measurement_acknowledged is True
    assert order.self_measurement_acknowledged_at is not None
    assert order.items[0].measurement_version.shirt_chest == Decimal("40.00")


def test_online_order_payment_reference_creates_pending_payment(client, db):
    s = _service(db)
    client.post(
        "/order",
        data={
            "name": "Online Customer",
            "mobile": "9555555555",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "fabric_source": "CUSTOMER",
            "payment_reference": "upi_ref_999",
        },
    )
    order = Order.query.filter_by(order_number="NST-0001").one()
    payment = Payment.query.filter_by(order_id=order.id).one()
    assert payment.status == PaymentStatus.PENDING  # never fabricated as verified
    assert payment.amount == order.required_advance
    assert payment.transaction_reference == "upi_ref_999"


def test_online_order_without_payment_reference_creates_no_payment(client, db):
    s = _service(db)
    client.post(
        "/order",
        data={
            "name": "Online Customer",
            "mobile": "9555555555",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "fabric_source": "CUSTOMER",
        },
    )
    order = Order.query.filter_by(order_number="NST-0001").one()
    assert Payment.query.filter_by(order_id=order.id).count() == 0


# --- Track order ---------------------------------------------------------


def test_track_order_with_correct_mobile(client, db):
    s = _service(db)
    client.post(
        "/order",
        data={
            "name": "Online Customer",
            "mobile": "9555555555",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "fabric_source": "CUSTOMER",
        },
    )
    resp = client.post(
        "/track-order", data={"order_number": "NST-0001", "mobile": "9555555555"}
    )
    assert resp.status_code == 200
    assert b"NST-0001" in resp.data


def test_track_order_wrong_mobile_does_not_confirm_existence(client, db):
    s = _service(db)
    client.post(
        "/order",
        data={
            "name": "Online Customer",
            "mobile": "9555555555",
            "items-0-service_id": str(s.id),
            "items-0-quantity": "1",
            "fabric_source": "CUSTOMER",
        },
    )
    resp = client.post(
        "/track-order", data={"order_number": "NST-0001", "mobile": "9999999999"}
    )
    assert resp.status_code == 200
    assert b"could not find" in resp.data.lower() or b"We could not find" in resp.data


def test_track_order_unknown_number(client, db):
    resp = client.post(
        "/track-order", data={"order_number": "NST-9999", "mobile": "9555555555"}
    )
    assert resp.status_code == 200
    assert b"We could not find" in resp.data
