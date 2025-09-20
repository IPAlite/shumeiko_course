from fastapi import HTTPException

from src.exceptions import AllRoomsAreBookedException, ObjectNotFoundException
from src.schemas.bookings import BookindAdd
from src.schemas.rooms import Room
from src.services.base import BaseService


class BookingsService(BaseService):
    async def get_all_bookings(self):
        return await self.db.bookings.get_all()

    async def get_user_bookings(self, user_id):
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def add_bookings(self, hotel_id, room_id, booking_data, user_id):
        try:
            room: Room = await self.db.rooms.get_one(id=room_id, hotel_id=hotel_id)
        except ObjectNotFoundException:
            raise HTTPException(status_code=404, detail="Номер не найден")

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
            await self.db.bookings.add_booking(booking_data)
        except AllRoomsAreBookedException as ex:
            raise HTTPException(status_code=409, detail=ex.detail)
        await self.db.commit()

        return booking_data
