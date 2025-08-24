from datetime import date

from fastapi import APIRouter, HTTPException, Body, Query

from src.schemas.rooms import RoomAddRequest, RoomAdd, RoomPatchRequest, RoomPatch
from src.schemas.facilities import RoomFacilityAdd, RoomFacilityPatch
from src.database import async_session_maker
from src.api.dependencies import DBDep

router = APIRouter(prefix='/hotels', tags=['Номера'])


@router.get("/{hotel_id}/rooms", summary='Получение всех номеров отеля')
async def get_all_rooms(hotel_id: int,
                     db: DBDep,
                     date_from: date = Query(example="2025-08-01"),
                     date_to: date = Query(example="2025-08-10")
                    ):
    return await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


@router.get("/{hotel_id}/rooms/{room_id}", summary='Получение конретного номера')
async def get_definite_room(hotel_id:int, room_id: int, db: DBDep):
    result = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    if result is None:
        raise HTTPException(status_code=404, detail='Такой комнаты не существует')
    return result


@router.post("/{hotel_id}/rooms", summary='Добавление номеров')
async def add_new_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body()):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)

    hotel = await db.hotels.get_one_or_none(id = hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail='Отель отсуствует в базе')
    
    rooms_facilities_data = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

    return {'status': 'ok', 'data': room}


@router.put('{hotel_id}/rooms/{room_id}', summary='Полное обновление информации о номере')
async def room_rewrite(hotel_id:int, room_id:int, room_data: RoomAddRequest, db: DBDep):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(id=room_id, data=_room_data)

    if room_data.facilities_ids is None:
        facilities_ids = []
    else:
        facilities_ids = room_data.facilities_ids

    if facilities_ids and facilities_ids[0] == 0:
        raise HTTPException(status_code=404, detail='Измените перечень удобств для текущего номера')
    
    _exsiting_facilities = await db.rooms_facilities.get_filtered(room_id=room_id)
    exsiting_facilities_ids = set([uid.facility_id for uid in _exsiting_facilities])

    add_facilities_ids = set(facilities_ids)

    ids_for_remove = exsiting_facilities_ids - add_facilities_ids
    ids_to_add = add_facilities_ids - exsiting_facilities_ids

    if facilities_ids:
        await db.rooms_facilities.delete_bulk(ids_for_remove, room_id=room_id)
    add_ids = [RoomFacilityPatch(room_id=room_id, facility_id=f_id) for f_id in ids_to_add]
    await db.rooms_facilities.add_bulk(add_ids)
    await db.commit()

    return {'status': 'ok'}


@router.patch('{hotel_id}/rooms/{room_id}', summary='Частичное обновление информации о номере')
async def room_change(hotel_id:int, room_id:int, room_data: RoomPatchRequest, db: DBDep):
    _room_data = RoomPatch(hotel_id=hotel_id, **room_data.model_dump(exclude_unset=True, exclude={'add_facilities', 'remove_facilities'}))
    await db.rooms.edit(id=room_id, hotel_id=hotel_id, data=_room_data, exclude_unset=True)
    
    room_data.add_facilities = [] if room_data.add_facilities and room_data.add_facilities[0] == 0 else room_data.add_facilities
    room_data.remove_facilities = [] if room_data.remove_facilities and room_data.remove_facilities[0] == 0 else room_data.remove_facilities

    _exsiting_facilities = await db.rooms_facilities.get_filtered(room_id=room_id)
    exsiting_facilities_ids = set([uid.facility_id for uid in _exsiting_facilities])
    
    ids_to_add = set(room_data.add_facilities) - exsiting_facilities_ids

    await db.rooms_facilities.delete_bulk(room_data.remove_facilities, room_id=room_id)
    add_ids = [RoomFacilityAdd(room_id=room_id, facility_id=f_id) for f_id in ids_to_add]
    await db.rooms_facilities.add_bulk(add_ids)
    await db.commit()

    return {'status': 'ok'}


@router.delete("/{hotel_id}/rooms/{room_id}", summary='Удаление комнаты')
async def room_delete(hotel_id: int, room_id: int, db: DBDep):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()
    return {'status': 'ok'}
