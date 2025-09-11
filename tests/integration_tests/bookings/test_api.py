import pytest


@pytest.fixture(scope='function')
async def db_clear(db):
    await db.bookings.delete_all()
    await db.commit()


@pytest.mark.parametrize("hotel_id, room_id, date_from, date_to, status_code", [
    (1, 1, "2025-08-01", "2025-08-10", 200),
    (1, 1, "2025-08-01", "2025-08-10", 200),
    (1, 1, "2025-08-01", "2025-08-10", 200),
    (1, 1, "2025-08-01", "2025-08-10", 200),
    (1, 1, "2025-08-01", "2025-08-10", 200),
    (1, 1, "2025-08-01", "2025-08-10", 409)
])
async def test_add_booking(authenticated_ac, hotel_id, room_id, date_from, date_to, status_code):
    response = await authenticated_ac.post(
        f"/bookings/{hotel_id}/{room_id}",
        json={
            "date_from": date_from,
            "date_to": date_to
        }
    )

    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res['status'] == 'ok'
        assert "booking_data" in res



@pytest.mark.parametrize("num_of_booking", [1, 2, 3])
async def test_add_and_get_my_booking(authenticated_ac, db_clear, num_of_booking, db):
    room = (await db.rooms.get_all())[0]
    for i in range(num_of_booking):
        date_from = f"2025-08-{i+1:02d}"
        date_to = f"2025-08-{i+5:02d}" 

        booking_resp = await authenticated_ac.post(
            f"/bookings/{room.hotel_id}/{room.id}",
            json={
                "date_from": date_from,
                "date_to": date_to
            }
        )
        assert booking_resp.status_code == 200

    response = await authenticated_ac.get("/bookings/me")
    bookings = response.json()

    assert response.status_code == 200
    assert len(bookings) == num_of_booking
