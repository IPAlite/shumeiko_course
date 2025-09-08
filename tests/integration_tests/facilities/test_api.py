async def test_add_facilities(ac):
    facility_title = "СПА"
    response = await ac.post(
        "/facilities",
        json={
            "title": facility_title
        }
    )
    res = response.json()
    assert isinstance(res, dict)
    assert res["data"]["title"] == facility_title
    assert "data" in res


async def test_get_facilities(ac):
    response = await ac.get("/facilities")
    print(f"{response.json()=}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
