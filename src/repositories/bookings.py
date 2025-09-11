from datetime import date

from fastapi import HTTPException

from sqlalchemy import insert, select, exists, and_
from sqlalchemy.orm import selectinload, joinedload

from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.base import BaseRepository
from src.models.bookings import BookingsOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.schemas.bookings import Booking, BookindAdd
from src.repositories.utils import rooms_ids_for_booking


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
    

    async def get_bookings_with_today_checkin(self):
        query = (
            select(BookingsOrm)
            .filter(BookingsOrm.date_from == date.today())
        )
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]
    

    async def add_booking(self, data: BookindAdd):
        rooms_ids_for_get = rooms_ids_for_booking(hotel_id=data.hotel_id, date_from=data.date_from, date_to=data.date_to)
        query = (
            select(RoomsOrm)
            .filter(
                RoomsOrm.id.in_(rooms_ids_for_get),
                RoomsOrm.hotel_id == data.hotel_id
            ) 
        )
        rooms_ids_for_book_res = await self.session.execute(query)
        rooms_ids_for_book: list[int] = rooms_ids_for_book_res.scalars().all()

        if data.room_id in [room.id for room in rooms_ids_for_book]:
            return await self.add(data)
        
        else:
            raise HTTPException(status_code=409, detail='Комната забронирована на данные даты')

        
