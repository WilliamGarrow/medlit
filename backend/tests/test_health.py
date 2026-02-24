def test_health_returns_200(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


def test_health_fhir_loaded(client):
    resp = client.get("/api/health")
    data = resp.json()["data"]
    assert data["fhir_data"] == "loaded"
    assert data["fhir_patients"] >= 1


def test_health_stub_mode(client):
    resp = client.get("/api/health")
    data = resp.json()["data"]
    assert data["ollama"] == "stub mode"
