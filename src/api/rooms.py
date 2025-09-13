from datetime import date

from fastapi import APIRouter, HTTPException, Body, Query
from fastapi_cache.decorator import cache

from src.exceptions import DateErrorException, HotelNotFoundHTTPException, ObjectNotFoundException, RoomNotFoundHTTPException
from src.schemas.rooms import RoomAddRequest, RoomAdd, RoomPatchRequest, RoomPatch
from src.schemas.facilities import RoomFacilityAdd
from src.api.dependencies import DBDep

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms", summary="Получение всех номеров отеля")
@cache(expire=10)
async def get_all_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2025-08-01"),
    date_to: date = Query(example="2025-08-10"),
):  
    try:
        room_resp =  await db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
    except DateErrorException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)

    return {"status": "ok", "data": room_resp}


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение конретного номера")
@cache(expire=10)
async def get_definite_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        result = await db.rooms.get_one_or_none_with_rels(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException
    return result


@router.post("/{hotel_id}/rooms", summary="Добавление номеров")
async def add_new_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body()):
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)

    rooms_facilities_data = [
        RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids
    ]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

    return {"status": "ok", "data": room}


@router.put("{hotel_id}/rooms/{room_id}", summary="Полное обновление информации о номере")
async def room_rewrite(hotel_id: int, room_id: int, room_data: RoomAddRequest, db: DBDep):
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException

    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException
    
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(id=room_id, data=_room_data)
    await db.rooms_facilities.set_room_facilities(
        room_id=room_id, facilities_ids=room_data.facilities_ids
    )
    await db.commit()
    return {"status": "ok"}


@router.patch("{hotel_id}/rooms/{room_id}", summary="Частичное обновление информации о номере")
async def room_change(hotel_id: int, room_id: int, room_data: RoomPatchRequest, db: DBDep):
    try:
        await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException
    
    _room_data_dict = room_data.model_dump(exclude_unset=True)
    _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
    await db.rooms.edit(id=room_id, hotel_id=hotel_id, data=_room_data, exclude_unset=True)

    if "facilities_ids" in _room_data_dict:
        await db.rooms_facilities.set_room_facilities(
            room_id=room_id, facilities_ids=_room_data_dict["facilities_ids"]
        )

    await db.commit()
    return {"status": "ok"}


@router.delete("/{hotel_id}/rooms/{room_id}", summary="Удаление комнаты")
async def room_delete(hotel_id: int, room_id: int, db: DBDep):
    try:
        await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    
    try:
        await db.rooms.get_one(id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException
    
    await db.commit()
    return {"status": "ok"}
