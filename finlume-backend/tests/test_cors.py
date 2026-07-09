def test_cors_allowed_origin(client):
    headers = {"Origin": "http://localhost:5173"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

def test_cors_disallowed_origin(client):
    headers = {"Origin": "http://evil-site.com"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") != "http://evil-site.com"
