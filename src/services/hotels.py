from datetime import date

from fastapi import HTTPException

from src.schemas.hotels import HotelAdd, HotelPatch
from src.exceptions import DateErrorException
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_hotels(
        self, pagination, location: str | None, title: str | None, date_from: date, date_to: date
    ):
        per_page = pagination.per_page or 5
        try:
            hotel_resp = await self.db.hotels.get_filtered_by_time(
                date_from=date_from,
                date_to=date_to,
                limit=per_page,
                offset=(pagination.page - 1) * per_page,
                location=location,
                title=title,
            )
        except DateErrorException as ex:
            raise HTTPException(status_code=400, detail=ex.detail)

        return {"status": "ok", "data": hotel_resp}

    async def get_hotel_by_id(self, hotel_id):
        return await self.db.hotels.get_one(id=hotel_id)

    async def add_hotel(self, hotel_data: HotelAdd):
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()
        return hotel

    async def change_hotel(self, hotel_id: int, hotel_data: HotelAdd):
        await self.db.hotels.edit(data=hotel_data, id=hotel_id, exclude_unset=False)
        await self.db.commit()

    async def rewrite_hotel(self, hotel_id: int, hotel_data: HotelPatch):
        await self.db.hotels.edit(data=hotel_data, id=hotel_id, exclude_unset=True)
        await self.db.commit()

    async def delete_hotel(self, hotel_id):
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
