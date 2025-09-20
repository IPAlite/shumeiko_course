from fastapi import APIRouter

from src.services.bookings import BookingsService
from src.schemas.bookings import BookingAddRequest
from src.api.dependencies import DBDep, UserIdDep


router = APIRouter(prefix="/bookings", tags=["Бронирование номеров"])


@router.get("", summary="Получение всех бронирований")
async def get_all_bookings(db: DBDep):
    return await BookingsService(db).get_all_bookings()


@router.get("/me", summary="Получение бронирований пользователя")
async def get_user_bookings(user_id: UserIdDep, db: DBDep):
    return await BookingsService(db).get_user_bookings(user_id)


@router.post("/{hotel_id}/{room_id}", summary="Добавление бронирования")
async def add_booking(
    hotel_id: int,
    room_id: int,
    booking_data: BookingAddRequest,
    db: DBDep,
    user_id: UserIdDep,
):
    booking_data = await BookingsService(db).add_bookings(hotel_id, room_id, booking_data, user_id)
    return {"status": "ok", "booking_data": booking_data}
