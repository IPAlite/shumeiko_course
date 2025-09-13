from fastapi import APIRouter, HTTPException

from src.exceptions import AllRoomsAreBookedException, ObjectNotFoundException
from src.schemas.bookings import BookingAddRequest, BookindAdd
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room



router = APIRouter(prefix="/bookings", tags=["Бронирование номеров"])


@router.get("", summary="Получение всех бронирований")
async def get_all_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me", summary="Получение бронирований пользователя")
async def get_user_bookings(user_id: UserIdDep, db: DBDep):
    return await db.bookings.get_filtered(user_id=user_id)


@router.post("/{hotel_id}/{room_id}", summary="Добавление бронирования")
async def add_booking(
    hotel_id: int,
    room_id: int,
    booking_data: BookingAddRequest,
    db: DBDep,
    user_id: UserIdDep,
):    
    try:
        room: Room = await db.rooms.get_one(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail='Номер не найден')
    
    days_different = (booking_data.date_to - booking_data.date_from).days
    room_price: int = room.price * days_different

    booking_data = BookindAdd(
        user_id=user_id,
        hotel_id=hotel_id,
        room_id=room_id,
        price=room_price,
        **booking_data.model_dump(),
    )
    try:
        await db.bookings.add_booking(booking_data)
    except AllRoomsAreBookedException as ex:
        raise HTTPException(status_code=409, detail=ex.detail)
    await db.commit()

    return {"status": "ok", "booking_data": booking_data}
