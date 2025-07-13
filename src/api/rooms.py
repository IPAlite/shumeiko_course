from fastapi import APIRouter, HTTPException, Query, Body

from src.repositories.rooms import RoomsRepository
from src.repositories.hotels import HotelsRepository
from src.schemas.rooms import RoomAdd, RoomEdit, RoomPatch
from src.database import async_session_maker

router = APIRouter(prefix='/by_hotels', tags=['Номера'])


@router.get("/{hotel_id}", summary='Получение всех номеров отеля')
async def get_all_rooms(
    hotel_id: int, 
    title: str | None = Query(None), 
    description: str | None = Query(None), 
    price: int | None = Query(None), 
    quantity: str | None = Query(None)
    ):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_all(
            hotel_id=hotel_id,
            title=title,
            description=description, 
            price=price,
            quantity=quantity
    )


@router.get("/{hotel_id}/{room_id}", summary='Получение конретного номера')
async def get_definite_room(hotel_id:int, room_id: int):
    async with async_session_maker() as session:
        result = await RoomsRepository(session).get_one_or_none(id=room_id, hotel_id=hotel_id)
        if result is None:
            raise HTTPException(status_code=404, detail='Такой комнаты не существует')


@router.post("", summary='Добавление номеров')
async def add_new_room(room_data: RoomAdd = Body(openapi_examples={
    "1": {"summary": "Базовый", "value": {
        "hotel_id": 1,
        "title": "Базовый номер",
        "description": "Есть все, что нужно, для комфортного времяпрепровождения",
        "price": 7500,
        "quantity": 12
    }},
    "2": {"summary": "Люкас", "value": {
        "hotel_id": 2,
        "title": "Дубайский люкс",
        "description": "Номер, в котором вы будете чувствовать себя королем",
        "price": 24500,
        "quantity": 3
    }}
})):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id = room_data.hotel_id)
        if hotel is None:
            raise HTTPException(status_code=404, detail='Отель отсуствует в базе')
        
        room = await RoomsRepository(session).add(room_data)
        await session.commit()
    return {'status': 'ok', 'data': room}


@router.put('{hotel_id}/{room_id}', summary='Полное обновление информации о номере')
async def room_rewrite(hotel_id:int, room_id:int, room_data: RoomEdit):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(id=room_id, data=room_data)
        await session.commit()
    return {'status': 'ok'}


@router.patch('{hotel_id}/{room_id}', summary='Частичное обновление информации о номере')
async def room_change(hotel_id:int, room_id:int, room_data: RoomPatch):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(id=room_id, data=room_data, exclude_unset=True)
        await session.commit()
    return {'status': 'ok'}


@router.delete("/{hotel_id}/{room_id}", summary='Удаление комнаты')
async def room_delete(hotel_id: int, room_id: int):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(hotel_id=hotel_id, id=room_id)
        await session.commit()
    return {'status': 'ok'}
