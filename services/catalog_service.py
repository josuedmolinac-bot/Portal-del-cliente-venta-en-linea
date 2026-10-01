from copy import deepcopy

from data.products import PRODUCTS


def get_availability(stock):
    if not isinstance(stock, int) or isinstance(stock, bool):
        raise ValueError("El stock debe ser un número entero.")
    if stock <= 0:
        return "Sin stock"
    if stock <= 5:
        return "Stock limitado"
    return "Disponible"


def _prepare_product(product):
    prepared = deepcopy(product)
    prepared["availability"] = get_availability(prepared["stock"])
    return prepared


def get_products():
    return [_prepare_product(product) for product in PRODUCTS]


def get_product_by_id(product_id):
    if not isinstance(product_id, int) or isinstance(product_id, bool) or product_id < 1:
        return None
    product = next((item for item in PRODUCTS if item["id"] == product_id), None)
    return _prepare_product(product) if product else None


def get_featured_products():
    return [_prepare_product(product) for product in PRODUCTS if product["featured"]]


def get_categories():
    return sorted({product["category"] for product in PRODUCTS})


def get_brands():
    return sorted({product["brand"] for product in PRODUCTS})

