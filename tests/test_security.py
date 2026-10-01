def test_malformed_product_identifier_is_not_coerced(client):
    response = client.get("/productos/1abc")
    assert response.status_code == 404
    assert b"Traceback" not in response.data


def test_security_headers_are_present(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
