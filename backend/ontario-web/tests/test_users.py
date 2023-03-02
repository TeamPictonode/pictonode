# GNU AGPL v3 License


def test_login_and_register(client):
    username = "test"
    password = "test"
    realname = "Test User"

    # Register a user
    response = client.post("/api/register", json={
        "username": username,
        "password": password,
        "realname": realname
    })
    assert response.status_code == 200
    assert response.json["success"]

    # Login with the user
    response = client.post("/api/login", json={
        "username": username,
        "password": password
    })
    assert response.status_code == 200
    assert response.json["success"]
