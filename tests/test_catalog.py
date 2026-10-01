from pathlib import Path

from data.products import PRODUCTS
from services.catalog_service import get_brands, get_categories, get_product_by_id, get_products


def test_catalog_has_ten_controlled_products():
    products = get_products()
    assert len(products) == 10
    assert len({item["id"] for item in products}) == 10
    assert [item["code"] for item in products] == [f"PROD-{number:03d}" for number in range(1, 11)]


def test_categories_and_brands_are_unique_and_sorted():
    assert get_categories() == sorted(set(get_categories()))
    assert get_brands() == sorted(set(get_brands()))
    assert "Alarmas" in get_categories()
    assert "SecureTech" in get_brands()


def test_product_lookup_rejects_invalid_identifiers():
    assert get_product_by_id(1)["code"] == "PROD-001"
    assert get_product_by_id("1") is None
    assert get_product_by_id("1abc") is None
    assert get_product_by_id(-1) is None
    assert get_product_by_id(999) is None


def test_service_returns_defensive_copies():
    item = get_product_by_id(1)
    item["price"] = 1
    item["features"].append("Manipulado")
    assert get_product_by_id(1)["price"] == 189990
    assert "Manipulado" not in get_product_by_id(1)["features"]


def test_all_declared_assets_exist():
    static_root = Path(__file__).parents[1] / "static"
    for item in PRODUCTS:
        for image in item["images"]:
            assert (static_root / image["path"]).is_file()
        for document in item["documents"]:
            assert (static_root / document["path"]).is_file()


def test_catalog_and_detail_routes(client):
    response = client.get("/productos")
    assert response.status_code == 200
    assert b"PROD-001" in response.data
    assert b"10 productos" in response.data
    detail = client.get("/productos/1")
    assert detail.status_code == 200
    assert "Panel de alarma".encode() in detail.data


def test_missing_and_malformed_product_routes_return_404(client):
    assert client.get("/productos/999").status_code == 404
    assert client.get("/productos/1abc").status_code == 404
    assert client.get("/ruta-inexistente").status_code == 404

