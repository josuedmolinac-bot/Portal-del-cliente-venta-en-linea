import pytest

from data.demo_user import DEMO_USER
from services.order_service import OrderValidationError, build_cart, validate_quantity
from services.catalog_service import get_product_by_id


DEMO_EMAIL = "cliente.demo@seguridad.local"
DEMO_PASSWORD = "DemoSegura2026!"


def login(client, email=DEMO_EMAIL, password=DEMO_PASSWORD):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_demo_user_stores_hash_not_plain_password():
    assert "password" not in DEMO_USER
    assert DEMO_PASSWORD not in DEMO_USER["password_hash"]
    assert DEMO_USER["password_hash"].startswith("scrypt:")


def test_valid_login_creates_minimal_session(client):
    response = login(client)
    assert response.status_code == 200
    assert "Mi cuenta".encode() in response.data
    with client.session_transaction() as session:
        assert session["user_id"] == DEMO_USER["id"]
        assert "password" not in session


@pytest.mark.parametrize(
    ("email", "password"),
    [("otro@seguridad.local", DEMO_PASSWORD), (DEMO_EMAIL, "incorrecta")],
)
def test_invalid_login_is_rejected(client, email, password):
    response = login(client, email, password)
    assert "Correo o contraseña de demostración incorrectos.".encode() in response.data
    with client.session_transaction() as session:
        assert "user_id" not in session


@pytest.mark.parametrize(
    "path", ["/cuenta", "/carrito", "/pedidos", "/pedidos/PED-DEMO-001"]
)
def test_protected_routes_redirect_to_login(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_logout_clears_session(client):
    login(client)
    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_add_product_and_cart_totals_use_controlled_price(client):
    login(client)
    response = client.post(
        "/carrito/agregar/1",
        data={"quantity": "2", "price": "1"},
        follow_redirects=True,
    )
    assert "fue agregado al carrito".encode() in response.data
    cart = client.get("/carrito")
    assert b"$379.980" in cart.data
    assert b">$1<" not in cart.data


def test_add_unknown_or_out_of_stock_product(client):
    login(client)
    assert client.post("/carrito/agregar/999", data={"quantity": "1"}).status_code == 404
    response = client.post(
        "/carrito/agregar/4", data={"quantity": "1"}, follow_redirects=True
    )
    assert "no tiene stock disponible".encode() in response.data


@pytest.mark.parametrize("quantity", ["0", "-1", "texto", "19"])
def test_invalid_cart_quantities_are_rejected(client, quantity):
    login(client)
    response = client.post(
        "/carrito/agregar/1",
        data={"quantity": quantity},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session.get("cart", {}) == {}


def test_update_and_remove_cart_item(client):
    login(client)
    client.post("/carrito/agregar/1", data={"quantity": "1"})
    client.post("/carrito/actualizar/1", data={"quantity": "3"})
    with client.session_transaction() as session:
        assert session["cart"]["1"] == 3
    response = client.post("/carrito/eliminar/1", follow_redirects=True)
    assert "Producto eliminado".encode() in response.data
    with client.session_transaction() as session:
        assert session["cart"] == {}


def test_cart_service_calculates_subtotal_and_total():
    items, total = build_cart({"1": 2, "2": 1})
    assert items[0]["subtotal"] == 189990 * 2
    assert total == (189990 * 2) + 24990


def test_confirm_order_and_view_tracking(client):
    login(client)
    client.post("/carrito/agregar/2", data={"quantity": "2"})
    response = client.post("/carrito/confirmar", follow_redirects=True)
    assert response.status_code == 200
    assert b"Estado actual" in response.data
    assert b"$49.980" in response.data
    with client.session_transaction() as session:
        assert session["cart"] == {}
        assert len(session["orders"]) == 1
        assert session["orders"][0]["user_id"] == DEMO_USER["id"]
        assert session["orders"][0]["total"] == 49980


def test_empty_order_is_rejected(client):
    login(client)
    response = client.post("/carrito/confirmar", follow_redirects=True)
    assert "carrito vacío".encode() in response.data


def test_demo_orders_show_all_tracking_states(client):
    login(client)
    response = client.get("/pedidos")
    assert response.status_code == 200
    for state in ("Recibido", "En preparación", "Despachado", "Entregado"):
        assert state.encode() in response.data


def test_order_detail_missing_or_owned_by_other_user_is_hidden(client):
    login(client)
    assert client.get("/pedidos/PED-DEMO-999").status_code == 404
    with client.session_transaction() as session:
        session["orders"] = [
            {
                "id": "PED-20261001-ABCDEF",
                "date": "2026-10-01",
                "status": "Recibido",
                "user_id": "another-user",
                "items": [{"product_id": 1, "quantity": 1}],
                "total": 189990,
            }
        ]
    assert client.get("/pedidos/PED-20261001-ABCDEF").status_code == 404
    assert client.get("/pedidos/../../secreto").status_code == 404


@pytest.mark.parametrize("value", ["", "0", "-1", "texto", "19"])
def test_quantity_validator_rejects_invalid_values(value):
    with pytest.raises(OrderValidationError):
        validate_quantity(value, get_product_by_id(1))
