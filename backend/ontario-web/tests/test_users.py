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


def test_list_users(client):
    username = "test2"
    password = "test2"
    realname = "Test User2"

    # Register a user
    response = client.post("/api/register", json={
        "username": username,
        "password": password,
        "realname": realname
    })
    assert response.status_code == 200
    assert response.json["success"]

    # List the users
    response = client.get("/api/users")
    assert response.status_code == 200

    users = response.json
    for uname, rname in users:
        if uname == username:
            assert rname == realname
            return
