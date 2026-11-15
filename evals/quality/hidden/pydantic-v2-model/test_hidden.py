import pytest
from pydantic import ValidationError

from orders.models import Item, Order


def test_valid_order_dumps_to_dict():
    order = Order(items=[Item(sku="a", qty=1)], email="x@example.com")
    assert order.model_dump() == {"items": [{"sku": "a", "qty": 1}], "email": "x@example.com"}


def test_email_without_at_is_rejected():
    with pytest.raises(ValidationError):
        Order(items=[], email="nope")


def test_item_is_still_frozen():
    with pytest.raises(ValidationError):
        Item(sku="a", qty=1).qty = 2
