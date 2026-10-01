from copy import deepcopy
from datetime import date
import secrets

from data.demo_orders import DEMO_ORDERS
from services.catalog_service import get_product_by_id


ORDER_STATES = ("Recibido", "En preparación", "Despachado", "Entregado")


class OrderValidationError(ValueError):
    pass


def validate_quantity(value, product):
    normalized = str(value or "").strip()
    if not normalized.isdecimal():
        raise OrderValidationError("La cantidad debe ser un número entero.")
    quantity = int(normalized)
    if quantity < 1:
        raise OrderValidationError("La cantidad mínima es 1.")
    if product["stock"] <= 0:
        raise OrderValidationError("El producto no tiene stock disponible.")
    if quantity > product["stock"]:
        raise OrderValidationError(
            f"La cantidad máxima disponible es {product['stock']}."
        )
    return quantity


def build_cart(cart_data):
    items = []
    total = 0
    for product_id, raw_quantity in (cart_data or {}).items():
        try:
            normalized_id = int(product_id)
        except (TypeError, ValueError):
            continue
        product = get_product_by_id(normalized_id)
        if product is None:
            continue
        try:
            quantity = validate_quantity(raw_quantity, product)
        except OrderValidationError:
            continue
        subtotal = product["price"] * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return items, total


def create_order(user_id, cart_data):
    items, total = build_cart(cart_data)
    if not items:
        raise OrderValidationError("No puedes confirmar un pedido con el carrito vacío.")
    return {
        "id": f"PED-{date.today():%Y%m%d}-{secrets.token_hex(3).upper()}",
        "date": date.today().isoformat(),
        "status": "Recibido",
        "user_id": user_id,
        "items": [
            {"product_id": item["product"]["id"], "quantity": item["quantity"]}
            for item in items
        ],
        "total": total,
    }


def enrich_order(order):
    enriched = deepcopy(order)
    items = []
    total = 0
    for item in enriched["items"]:
        product = get_product_by_id(item["product_id"])
        if product is None:
            continue
        subtotal = product["price"] * item["quantity"]
        items.append(
            {"product": product, "quantity": item["quantity"], "subtotal": subtotal}
        )
        total += subtotal
    enriched["items"] = items
    enriched["total"] = total
    enriched["state_index"] = ORDER_STATES.index(enriched["status"])
    return enriched


def get_orders_for_user(user_id, session_orders=None):
    all_orders = [*DEMO_ORDERS, *(session_orders or [])]
    orders = [
        enrich_order(order) for order in all_orders if order["user_id"] == user_id
    ]
    return sorted(orders, key=lambda order: order["date"], reverse=True)


def get_order_for_user(order_id, user_id, session_orders=None):
    return next(
        (
            order
            for order in get_orders_for_user(user_id, session_orders)
            if order["id"] == order_id
        ),
        None,
    )
