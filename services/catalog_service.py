from copy import deepcopy
import unicodedata

from data.products import PRODUCTS
from utils.validators import (
    AVAILABILITY_OPTIONS,
    is_positive_integer,
    normalize_search_text,
    parse_non_negative_price,
    validate_choice,
    validate_price_range,
)


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
    if not is_positive_integer(product_id):
        return None
    product = next((item for item in PRODUCTS if item["id"] == product_id), None)
    return _prepare_product(product) if product else None


def get_featured_products():
    return [_prepare_product(product) for product in PRODUCTS if product["featured"]]


def get_categories():
    return sorted({product["category"] for product in PRODUCTS})


def get_brands():
    return sorted({product["brand"] for product in PRODUCTS})


def _searchable_text(value):
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def get_search_suggestions():
    suggestions = []
    for product in PRODUCTS:
        suggestions.extend((product["name"], product["code"]))
    return suggestions


def filter_products(parameters):
    categories = get_categories()
    brands = get_brands()
    filters = {
        "q": normalize_search_text(parameters.get("q")),
        "category": validate_choice(
            parameters.get("category"), categories, "La categoría"
        ),
        "brand": validate_choice(parameters.get("brand"), brands, "La marca"),
        "availability": validate_choice(
            parameters.get("availability"),
            AVAILABILITY_OPTIONS,
            "La disponibilidad",
        ),
        "min_price": parse_non_negative_price(
            parameters.get("min_price"), "El precio mínimo"
        ),
        "max_price": parse_non_negative_price(
            parameters.get("max_price"), "El precio máximo"
        ),
    }
    validate_price_range(filters["min_price"], filters["max_price"])

    products = get_products()
    if filters["q"]:
        query = _searchable_text(filters["q"])
        products = [
            product
            for product in products
            if query
            in _searchable_text(
                " ".join(
                    [
                        product["name"],
                        product["code"],
                        product["brand"],
                        product["category"],
                        product["description"],
                        *product["features"],
                    ]
                )
            )
        ]
    if filters["category"]:
        products = [
            product for product in products
            if product["category"] == filters["category"]
        ]
    if filters["brand"]:
        products = [
            product for product in products if product["brand"] == filters["brand"]
        ]
    if filters["availability"]:
        products = [
            product for product in products
            if product["availability"] == filters["availability"]
        ]
    if filters["min_price"] is not None:
        products = [
            product for product in products
            if product["price"] >= filters["min_price"]
        ]
    if filters["max_price"] is not None:
        products = [
            product for product in products
            if product["price"] <= filters["max_price"]
        ]
    return products, filters
