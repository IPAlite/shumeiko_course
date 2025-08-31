from datetime import date

from sqlalchemy import select, exists, and_

from repositories.mappers.mappers import BookingDataMapper
from src.repositories.base import BaseRepository
from src.models.bookings import BookingsOrm
from src.schemas.bookings import Booking

class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def has_overlap(self, hotel_id: int, room_id: int, date_from: date, date_to:date) -> bool:
        query = select(
            exists().where(
                and_(
                    self.model.room_id == room_id, 
                    self.model.hotel_id == hotel_id,
                    self.model.date_from < date_to,
                    self.model.date_to > date_from
                )
            )
        )

        return (await self.session.execute(query)).scalar()