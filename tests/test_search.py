import pytest

from services.catalog_service import filter_products, get_search_suggestions
from utils.validators import FilterValidationError


def codes(parameters):
    products, _filters = filter_products(parameters)
    return {product["code"] for product in products}


def test_search_by_full_and_partial_name():
    assert codes({"q": "Panel de alarma"}) == {"PROD-001"}
    assert codes({"q": "movimiento"}) == {"PROD-002"}


def test_search_by_code_is_case_insensitive():
    assert codes({"q": "prod-003"}) == {"PROD-003"}
    assert codes({"q": "PROD-003"}) == {"PROD-003"}


def test_search_by_keyword_and_without_accents():
    assert "PROD-003" in codes({"q": "camara"})
    assert {"PROD-003", "PROD-004"} <= codes({"q": "videovigilancia"})
    assert "PROD-010" in codes({"q": "sobrecarga"})


def test_filter_by_category_and_brand():
    assert codes({"category": "Alarmas"}) == {"PROD-001", "PROD-007"}
    assert codes({"brand": "AccessPro"}) == {"PROD-005", "PROD-006"}


@pytest.mark.parametrize(
    ("availability", "expected"),
    [
        ("Disponible", {"PROD-001", "PROD-002", "PROD-005", "PROD-007", "PROD-010"}),
        ("Stock limitado", {"PROD-003", "PROD-006", "PROD-009"}),
        ("Sin stock", {"PROD-004", "PROD-008"}),
    ],
)
def test_filter_by_availability(availability, expected):
    assert codes({"availability": availability}) == expected


def test_filter_by_minimum_and_maximum_price():
    assert codes({"min_price": "200000"}) == {"PROD-004"}
    assert codes({"max_price": "30000"}) == {"PROD-002", "PROD-009"}


def test_combined_filters():
    assert codes(
        {
            "q": "interior",
            "category": "Control de acceso",
            "brand": "AccessPro",
            "availability": "Disponible",
            "min_price": "80000",
            "max_price": "100000",
        }
    ) == {"PROD-005"}


def test_empty_search_returns_full_catalog():
    assert len(codes({"q": "   "})) == 10


@pytest.mark.parametrize(
    "parameters",
    [
        {"q": "x" * 101},
        {"category": "Categoría inexistente"},
        {"brand": "Marca inexistente"},
        {"availability": "Inventado"},
        {"min_price": "texto"},
        {"max_price": "-1"},
        {"min_price": "100", "max_price": "10"},
    ],
)
def test_invalid_filters_are_rejected(parameters):
    with pytest.raises(FilterValidationError):
        filter_products(parameters)


def test_suggestions_include_names_and_codes():
    suggestions = get_search_suggestions()
    assert "Panel de alarma híbrido AX-8" in suggestions
    assert "PROD-001" in suggestions


def test_catalog_route_searches_and_shows_empty_message(client):
    response = client.get("/productos?q=PROD-001")
    assert response.status_code == 200
    assert b"PROD-001" in response.data
    assert b'href="/productos/2"' not in response.data

    empty = client.get("/productos?q=no-existe")
    assert empty.status_code == 200
    assert "No encontramos productos que coincidan con tu búsqueda.".encode() in empty.data


def test_catalog_route_rejects_invalid_filters_with_friendly_error(client):
    response = client.get("/productos?category=Falsa")
    assert response.status_code == 400
    assert "La categoría no es válido.".encode() in response.data
    assert b"Traceback" not in response.data


def test_catalog_without_parameters_clears_filters(client):
    response = client.get("/productos")
    assert response.status_code == 200
    assert b"10 productos" in response.data
    assert b'value=""' in response.data


def test_datalist_and_home_search_are_functional(client):
    catalog = client.get("/productos")
    assert b'<datalist id="product-suggestions">' in catalog.data
    assert b'<option value="PROD-001">' in catalog.data

    home = client.get("/")
    assert home.status_code == 200
    assert b'action="/productos"' in home.data
    assert b'name="q"' in home.data
    assert b'type="search" list="home-suggestions" maxlength="100"' in home.data


def test_user_search_text_is_escaped(client):
    response = client.get("/productos?q=%3Cscript%3Ealert(1)%3C/script%3E")
    assert response.status_code == 200
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;" in response.data
