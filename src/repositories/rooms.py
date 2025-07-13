from sqlalchemy import select, func

from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.schemas.rooms import Room

class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_all(self, hotel_id, title, description, price, quantity) -> list[Room]:
        query = select(RoomsOrm).filter_by(hotel_id=hotel_id)

        if title:
            query = query.filter(func.lower(RoomsOrm.title).like(f'%{title.lower()}%'))
        if description:
            query = query.filter(func.lower(RoomsOrm.description).like(f'%{description.lower()}%'))
        if price:
            query = query.filter(RoomsOrm.price == price)
        if quantity:
            query = query.filter(RoomsOrm.quantity == quantity)


        print(query)

        result = await self.session.execute(query)

        return [Room.model_validate(room, from_attributes=True) for room in result.scalars().all()]
        