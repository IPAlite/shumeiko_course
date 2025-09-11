from fastapi import APIRouter, HTTPException

from src.schemas.bookings import BookingAddRequest, BookindAdd
from src.api.dependencies import DBDep, UserIdDep


router = APIRouter(prefix='/bookings', tags=['Бронирование номеров'])


@router.get('', summary='Получение всех бронирований')
async def get_all_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get('/me', summary='Получение бронирований пользователя')
async def get_user_bookings(user_id: UserIdDep, db: DBDep):
    return await db.bookings.get_filtered(user_id=user_id)


@router.post("/{hotel_id}/{room_id}", summary='Добавление бронирования')
async def add_booking(hotel_id:int, room_id:int, booking_data: BookingAddRequest, db: DBDep, user_id: UserIdDep):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail='Отель отсуствет в базе')
    
    days_different  = (booking_data.date_to - booking_data.date_from).days

    room = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    if room is None:
        raise HTTPException(status_code=404, detail='Комната отсуствет в базе')
    room_price: int = room.price * days_different
    
    booking_data = BookindAdd(user_id=user_id, hotel_id=hotel_id, room_id=room_id, price=room_price, **booking_data.model_dump())

    await db.bookings.add_booking(booking_data)
    await db.commit()

    return {'status': 'ok', 'booking_data': booking_data}