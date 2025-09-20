from datetime import date

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from src.services.rooms import RoomsService
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest
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
    room_resp = await RoomsService(db).get_all_rooms(hotel_id, date_from, date_to)
    return {"status": "ok", "data": room_resp}


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение конретного номера")
@cache(expire=10)
async def get_definite_room(hotel_id: int, room_id: int, db: DBDep):
    result = await RoomsService(db).get_definite_room(hotel_id, room_id)
    return result


@router.post("/{hotel_id}/rooms", summary="Добавление номеров")
async def add_new_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body()):
    room = await RoomsService(db).add_new_room(hotel_id, room_data)
    return {"status": "ok", "data": room}


@router.put("{hotel_id}/rooms/{room_id}", summary="Полное обновление информации о номере")
async def room_rewrite(hotel_id: int, room_id: int, room_data: RoomAddRequest, db: DBDep):
    await RoomsService(db).room_rewrite(hotel_id, room_id, room_data)
    return {"status": "ok"}


@router.patch("{hotel_id}/rooms/{room_id}", summary="Частичное обновление информации о номере")
async def room_change(hotel_id: int, room_id: int, room_data: RoomPatchRequest, db: DBDep):
    await RoomsService(db).room_change(hotel_id, room_id, room_data)
    return {"status": "ok"}


@router.delete("/{hotel_id}/rooms/{room_id}", summary="Удаление комнаты")
async def room_delete(hotel_id: int, room_id: int, db: DBDep):
    await RoomsService(db).room_delete(hotel_id, room_id)
    return {"status": "ok"}
