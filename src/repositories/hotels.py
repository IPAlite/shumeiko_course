from datetime import date

from sqlalchemy import select, func

from src.repositories.base import BaseRepository
from src.repositories.utils import rooms_ids_for_booking
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

    async def get_filtered_by_time(
            self,
            date_from: date,
            date_to: date,
            limit: int, 
            offset: int,
            location: str| None = None,
            title: str | None = None
    ):
        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )
        query = select(HotelsOrm).where(HotelsOrm.id.in_(select(hotels_ids_to_get.c.hotel_id)))

        if location:
            query = query.filter(HotelsOrm.location.ilike(f"%{location}%"))
        if title:
            query = query.filter(HotelsOrm.title.ilike(f"%{title}%"))

        query = query.order_by(HotelsOrm.id.asc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        hotels = result.scalars().all()
        return [self.schema.model_validate(h, from_attributes=True) for h in hotels]
