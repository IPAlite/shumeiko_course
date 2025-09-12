import pytest

from tests.conftest import get_db_null_pool


@pytest.fixture(scope="module")
async def db_clear():
    async for _db in get_db_null_pool():
        await _db.bookings.delete_all()
        await _db.commit()


@pytest.mark.parametrize(
    "hotel_id, room_id, date_from, date_to, status_code",
    [
        (1, 1, "2025-08-01", "2025-08-10", 200),
        (1, 1, "2025-08-01", "2025-08-10", 200),
        (1, 1, "2025-08-01", "2025-08-10", 200),
        (1, 1, "2025-08-01", "2025-08-10", 200),
        (1, 1, "2025-08-01", "2025-08-10", 200),
        (1, 1, "2025-08-01", "2025-08-10", 409),
    ],
)
async def test_add_booking(authenticated_ac, hotel_id, room_id, date_from, date_to, status_code):
    response = await authenticated_ac.post(
        f"/bookings/{hotel_id}/{room_id}",
        json={"date_from": date_from, "date_to": date_to},
    )

    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "ok"
        assert "booking_data" in res


@pytest.mark.parametrize(
    "hotel_id, room_id, date_from, date_to, booked_rooms",
    [
        (1, 1, "2025-08-01", "2025-08-10", 1),
        (1, 1, "2025-08-01", "2025-08-10", 2),
        (1, 1, "2025-08-01", "2025-08-10", 3),
    ],
)
async def test_add_and_get_my_booking(
    hotel_id, room_id, date_from, date_to, booked_rooms, db_clear, authenticated_ac
):
    response = await authenticated_ac.post(
        f"/bookings/{hotel_id}/{room_id}",
        json={"date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200

    response_my_bookings = await authenticated_ac.get("/bookings/me")
    assert response_my_bookings.status_code == 200
    assert len(response_my_bookings.json()) == booked_rooms
