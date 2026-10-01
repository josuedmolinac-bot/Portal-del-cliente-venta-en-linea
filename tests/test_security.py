def test_malformed_product_identifier_is_not_coerced(client):
    response = client.get("/productos/1abc")
    assert response.status_code == 404
    assert b"Traceback" not in response.data


def test_security_headers_are_present(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_cookie_security_configuration(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is False
    assert app.config["MAX_CONTENT_LENGTH"] == 16 * 1024


def test_csrf_rejects_post_without_token():
    from app import create_app

    protected_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "csrf-test-key",
            "WTF_CSRF_ENABLED": True,
        }
    )
    response = protected_app.test_client().post(
        "/login",
        data={"email": "cliente.demo@seguridad.local", "password": "DemoSegura2026!"},
    )
    assert response.status_code == 400
    assert "solicitud no pudo validarse".encode() in response.data
