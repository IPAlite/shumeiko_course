from fastapi import HTTPException

from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomPatch
from src.exceptions import (
    DateErrorException,
    HotelNotFoundHTTPException,
    ObjectNotFoundException,
    RoomNotFoundHTTPException,
)
from src.services.base import BaseService


class RoomsService(BaseService):
    async def get_all_rooms(self, hotel_id, date_from, date_to):
        try:
            room_resp = await self.db.rooms.get_filtered_by_time(
                hotel_id=hotel_id, date_from=date_from, date_to=date_to
            )
        except DateErrorException as ex:
            raise HTTPException(status_code=400, detail=ex.detail)

        return room_resp

    async def get_definite_room(self, hotel_id, room_id):
        try:
            result = await self.db.rooms.get_one_or_none_with_rels(id=room_id, hotel_id=hotel_id)
        except ObjectNotFoundException:
            raise RoomNotFoundHTTPException

        return result

    async def add_new_room(self, hotel_id, room_data):
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundHTTPException

        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room = await self.db.rooms.add(_room_data)

        rooms_facilities_data = [
            RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids
        ]
        await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()

        return room

    async def room_rewrite(self, hotel_id, room_id, room_data):
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundHTTPException

        try:
            await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundHTTPException

        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        await self.db.rooms.edit(id=room_id, data=_room_data)
        await self.db.rooms_facilities.set_room_facilities(
            room_id=room_id, facilities_ids=room_data.facilities_ids
        )
        await self.db.commit()

    async def room_change(self, hotel_id, room_id, room_data):
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundHTTPException

        try:
            await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundHTTPException

        _room_data_dict = room_data.model_dump(exclude_unset=True)
        _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
        await self.db.rooms.edit(id=room_id, hotel_id=hotel_id, data=_room_data, exclude_unset=True)

        if "facilities_ids" in _room_data_dict:
            await self.db.rooms_facilities.set_room_facilities(
                room_id=room_id, facilities_ids=_room_data_dict["facilities_ids"]
            )

        await self.db.commit()

    async def room_delete(self, hotel_id, room_id):
        try:
            await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        except ObjectNotFoundException:
            raise HotelNotFoundHTTPException

        try:
            await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundHTTPException

        await self.db.commit()
