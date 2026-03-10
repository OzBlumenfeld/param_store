import pytest
from fastapi.testclient import TestClient
def get_auth_token(client, username, password):
    # Register first
    client.post("/auth/register", json={
        "username": username,
        "password": password
    })
    # Login
    response = client.post("/auth/login", data={
        "username": username,
        "password": password
    })
    return response.json()["access_token"]

def test_parameter_lifecycle(client):
    token = get_auth_token(client, "user1", "password_1")
    headers = {"Authorization": f"Bearer {token}"}
    
    param_app = "test_app"
    param_name = "test_key"
    param_value = "api_secret_123"

    # 1. Create parameter
    response = client.post("/params/", json={"app": param_app, "name": param_name, "value": param_value}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == param_name

    # 2. List parameters
    response = client.get("/params/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == param_name

    # 3. Get parameter value
    response = client.get(f"/params/{param_name}?app={param_app}", headers=headers)
    assert response.status_code == 200
    assert response.json()["value"] == param_value

    # 4. Update parameter
    new_value = "new_secret_456"
    response = client.put(f"/params/{param_name}?app={param_app}", json={"value": new_value}, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Parameter updated successfully"

    # 5. Get updated parameter value
    response = client.get(f"/params/{param_name}?app={param_app}", headers=headers)
    assert response.status_code == 200
    assert response.json()["value"] == new_value

    # 6. Delete parameter
    response = client.delete(f"/params/{param_name}?app={param_app}", headers=headers)
    assert response.status_code == 200

    # 7. Verify it's gone
    response = client.get(f"/params/{param_name}?app={param_app}", headers=headers)
    assert response.status_code == 404

    # 8. Try updating non-existent parameter
    response = client.put(f"/params/{param_name}?app={param_app}", json={"value": "should_fail"}, headers=headers)
    assert response.status_code == 404

def test_api_isolation(client):
    token1 = get_auth_token(client, "user_a", "password_a")
    token2 = get_auth_token(client, "user_b", "password_b")
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # User A sets a param
    client.post("/params/", json={"app": "app", "name": "key", "value": "val_a"}, headers=headers1)
    
    # User B sets same param name
    client.post("/params/", json={"app": "app", "name": "key", "value": "val_b"}, headers=headers2)
    
    # Verify User A still sees val_a
    response = client.get("/params/key?app=app", headers=headers1)
    assert response.json()["value"] == "val_a"
    
    # Verify User B still sees val_b
    response = client.get("/params/key?app=app", headers=headers2)
    assert response.json()["value"] == "val_b"
