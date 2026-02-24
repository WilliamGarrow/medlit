def test_list_patients(client):
    resp = client.get("/api/patients")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 4


def test_get_patient_detail(client):
    resp = client.get("/api/patients/maria_garcia")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Maria Garcia"
    assert len(body["data"]["conditions"]) == 2
    assert len(body["data"]["medications"]) == 2


def test_get_patient_not_found(client):
    resp = client.get("/api/patients/nobody")
    assert resp.status_code == 404
