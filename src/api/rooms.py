from fastapi import APIRouter, HTTPException, Body

from src.schemas.rooms import RoomAddRequest, RoomAdd, RoomPatchRequest, RoomPatch
from src.database import async_session_maker
from src.api.dependencies import DBDep

router = APIRouter(prefix='/hotels', tags=['Номера'])


@router.get("/{hotel_id}/rooms", summary='Получение всех номеров отеля')
async def get_all_rooms(hotel_id: int, db: DBDep):
    return await db.rooms.get_filtered(hotel_id=hotel_id)


@router.get("/{hotel_id}/rooms/{room_id}", summary='Получение конретного номера')
async def get_definite_room(hotel_id:int, room_id: int, db: DBDep):
    result = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    if result is None:
        raise HTTPException(status_code=404, detail='Такой комнаты не существует')
    return result


@router.post("/{hotel_id}/rooms", summary='Добавление номеров')
async def add_new_room(hotel_id: int, db: DBDep, room_data: RoomAddRequest = Body(openapi_examples={
    "1": {"summary": "Базовый", "value": {
        "title": "Базовый номер",
        "description": "Есть все, что нужно, для комфортного времяпрепровождения",
        "price": 7500,
        "quantity": 12
    }},
    "2": {"summary": "Люкас", "value": {
        "title": "Дубайский люкс",
        "description": "Номер, в котором вы будете чувствовать себя королем",
        "price": 24500,
        "quantity": 3
    }}
})):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    hotel = await db.hotels.get_one_or_none(id = hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail='Отель отсуствует в базе')
    room = await db.rooms.add(_room_data)
    await db.commit()
    return {'status': 'ok', 'data': room}


@router.put('{hotel_id}/rooms/{room_id}', summary='Полное обновление информации о номере')
async def room_rewrite(hotel_id:int, room_id:int, room_data: RoomAddRequest, db: DBDep):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(id=room_id, data=_room_data)
    await db.commit()
    return {'status': 'ok'}


@router.patch('{hotel_id}/rooms/{room_id}', summary='Частичное обновление информации о номере')
async def room_change(hotel_id:int, room_id:int, room_data: RoomPatchRequest, db: DBDep):
    _room_data = RoomPatch(hotel_id=hotel_id, **room_data.model_dump(exclude_unset=True))
    await db.rooms.edit(id=room_id, hotel_id=hotel_id, data=_room_data, exclude_unset=True)
    await db.commit()
    return {'status': 'ok'}


@router.delete("/{hotel_id}/rooms/{room_id}", summary='Удаление комнаты')
async def room_delete(hotel_id: int, room_id: int, db: DBDep):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()
    return {'status': 'ok'}
