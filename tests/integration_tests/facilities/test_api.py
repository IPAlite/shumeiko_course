

async def test_add_facilities(ac):
    await ac.post(
        "/facilities",
        json={
            "title": "СПА"
        }
    )


async def test_get_facilities(ac):
    response = await ac.get("/facilities")
    print(f"{response.json()=}")
    assert response.status_code == 200
