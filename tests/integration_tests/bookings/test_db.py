from datetime import date

from src.database import async_session_maker_null_pool
from src.schemas.bookings import BookindAdd, BookingPatch

async def test_booking_crud(db):
    # create
    user_id = (await db.users.get_all())[0].id
    hotel_id = (await db.hotels.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id

    booking_data = BookindAdd(
        user_id = user_id,
        hotel_id = hotel_id,
        room_id = room_id,
        date_from = date(year=2025, month=9, day=1),
        date_to = date(year=2025, month=9, day=5),
        price = 500
    )
    new_booking = await db.bookings.add(booking_data)

    # read
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking
    assert booking.id == new_booking.id
    assert booking.room_id == new_booking.room_id
    assert booking.user_id == new_booking.user_id

    # update
    booking_data = BookingPatch(
        price=15000
    )
    await db.bookings.edit(booking_data, id=booking.id, exclude_unset=True)
    updated_booking = await db.bookings.get_one_or_none(id=booking.id)
    assert updated_booking
    assert updated_booking.user_id == user_id
    assert updated_booking.price != booking.price

    # delete
    booking_id = (await db.bookings.get_all())[0].id
    await db.bookings.delete(id=booking_id)
