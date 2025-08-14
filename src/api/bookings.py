from fastapi import APIRouter, HTTPException

from src.schemas.bookings import BookingAddRequest, BookindAdd
from src.api.dependencies import DBDep, UserIdDep


router = APIRouter(prefix='/bookings', tags=['Бронирование номеров'])

@router.post("/{hotel_id}/{room_id}", summary='Добавление бронирования')
async def create_bookin(hotel_id:int, room_id:int, booking_data: BookingAddRequest, db: DBDep, user_id: UserIdDep):
    days_different  = (booking_data.date_to - booking_data.date_from).days
    if days_different <= 0:
        raise HTTPException(status_code=422, detail='Проверьте даты бронирования')
    
    conflicts = await db.bookings.has_overlap(room_id=room_id, hotel_id=hotel_id, date_from=booking_data.date_from, date_to=booking_data.date_to)

    if conflicts:
        raise HTTPException(status_code=409, detail="Комната занята на выбранные дни")
    
    one_day_price = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    if one_day_price is None:
        raise HTTPException(status_code=404, detail='Комната отсуствет в базе')
    total_price = one_day_price.price * days_different
    
    booking_data = BookindAdd(user_id=user_id, hotel_id=hotel_id, room_id=room_id, price=total_price, **booking_data.model_dump())

    await db.bookings.add(booking_data)
    await db.commit()

    return {'status': 'ok', 'booking_data': booking_data}