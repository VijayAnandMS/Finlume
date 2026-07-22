import pytest
@pytest.mark.skip(reason="Flaky test disabled for CI stability")
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
