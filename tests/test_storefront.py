"""Storefront prices and tracking reflect server-side records, never UI guesses."""
from decimal import Decimal

import pytest

from app.models.customer import Customer
from app.models.enums import FabricSource, OrderPriority, OrderStatus, ServiceCategory
from app.models.service import Service
from app.services.order_service import create_order, update_status


def test_homepage_uses_current_active_catalogue_prices(client, db):
    service = Service(
        code="SHIRT_PANT_COMBO", name_en="Combo", category=ServiceCategory.SHIRT,
        default_stitching_price=Decimal("612.50"), is_active=True,
    )
    db.session.add(service)
    db.session.commit()
    assert "₹612.50" in client.get("/").text
    service.default_stitching_price = Decimal("675.25")
    db.session.commit()
    html = client.get("/").text
    assert "₹675.25" in html and "₹612.50" not in html
    service.is_active = False
    db.session.commit()
    assert "₹675.25" not in client.get("/").text


@pytest.mark.parametrize("status", list(OrderStatus))
def test_tracking_current_step_matches_saved_status_and_requires_mobile(client, db, status):
    customer = Customer(name="Tracking customer", mobile="9555555544")
    db.session.add(customer)
    db.session.commit()
    order = create_order(
        customer=customer,
        items=[{"service_name": "Shirt", "category": ServiceCategory.SHIRT,
                "quantity": 1, "stitching_price": Decimal("550.00")}],
        fabric_source=FabricSource.CUSTOMER, priority=OrderPriority.NORMAL,
        notes=None, actor_id=None,
    )
    update_status(order, status, actor_id=None)
    response = client.post("/track-order", data={
        "order_number": order.order_number, "mobile": customer.mobile,
    })
    assert response.status_code == 200
    from html.parser import HTMLParser

    class CurrentStepParser(HTMLParser):
        current = False
        label = ""
        def handle_starttag(self, tag, attrs):
            if tag == "li" and dict(attrs).get("aria-current") == "step":
                self.current = True
        def handle_endtag(self, tag):
            if tag == "li":
                self.current = False
        def handle_data(self, data):
            if self.current:
                self.label += data

    parser = CurrentStepParser()
    parser.feed(response.text)
    expected = {OrderStatus.NEW: "Order confirmed", OrderStatus.MEASUREMENT: "Measurement",
                OrderStatus.READY: "Ready for collection", OrderStatus.DELIVERED: "Delivered"}
    assert expected[status] in parser.label
    wrong = client.post("/track-order", data={
        "order_number": order.order_number, "mobile": "9555555533",
    })
    assert 'aria-current="step"' not in wrong.text
    assert "550.00" not in wrong.text
