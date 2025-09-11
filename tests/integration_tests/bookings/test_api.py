async def test_add_booking(db, authenticated_ac):
    room = (await db.rooms.get_all())[0]
    response = await authenticated_ac.post(
        f"/bookings/{room.hotel_id}/{room.id}",
        json={
            "date_from": "2025-08-01",
            "date_to": "2025-08-10"
        }
    )

    res = response.json()
    assert isinstance(res, dict)
    assert res['status'] == 'ok'
    assert "booking_data" in res