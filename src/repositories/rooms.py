from datetime import date

from sqlalchemy import select, func

from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.schemas.rooms import Room
from src.models.bookings import BookingsOrm
from src.database import engine
from src.repositories.utils import rooms_ids_for_booking

class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_filtered_by_time(self, hotel_id:int, date_from: date, date_to: date):
        rooms_ids_to_get = rooms_ids_for_booking(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
        return await self.get_filtered(RoomsOrm.id.in_(rooms_ids_to_get.scalar_subquery()))