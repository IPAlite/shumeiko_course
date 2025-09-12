import pytest


@pytest.mark.parametrize(
    "first_name, last_name, nikname, phone, email, password",
    [("Гусь", "Уткович", "AlonMneVlom", "8800553535", "user1@example.com", "string")],
)
async def test_auth_funcs(first_name, last_name, nikname, phone, email, password, ac):
    # register
    reg_response = await ac.post(
        "/auth/register",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "nikname": nikname,
            "phone": phone,
            "email": email,
            "password": password,
        },
    )
    assert reg_response.status_code == 200

    # login
    log_response = await ac.post("/auth/login", json={"email": email, "password": password})
    assert log_response.status_code == 200
    assert log_response.json().get("access_token")

    # me
    me_response = await ac.get("/auth/me")
    a_t = me_response.json()
    assert me_response.status_code == 200
    assert nikname == a_t.get("nikname")
    assert phone == a_t.get("phone")
    assert email == a_t.get("email")

    # logout
    logout_response = await ac.post("/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.cookies.get("access_token") is None

    # duplicate register
    duplicate_reg_response = await ac.post(
        "/auth/register",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "nikname": nikname,
            "phone": phone,
            "email": email,
            "password": password,
        },
    )
    assert duplicate_reg_response.status_code == 409

    # login with wrong_data
    log_response = await ac.post(
        "/auth/login", json={"email": "wrong_email", "password": "wrong_password"}
    )
    assert log_response.status_code == 422

    # check session after logout
    me_response_after_logout = await ac.get("/auth/me")
    a_t = me_response_after_logout.json()
    assert me_response_after_logout.status_code == 401

    # user delete with wrong email
    delete_response = await ac.delete("/auth/delete/wrong_email")
    assert delete_response.status_code == 404

    # user delete
    delete_response = await ac.delete(f"/auth/delete/{email}")
    assert delete_response.status_code == 200
