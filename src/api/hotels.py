from fastapi import Query, Body, APIRouter

from sqlalchemy import insert, select, func

from schemas.hotels import Hotel, HotelPatch
from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.repositories.hotels import HotelsRepository


router = APIRouter(prefix='/hotels', tags=['Отели'])



@router.get('', summary='Получение информации об отелях')
async def get_hotels(
    pagination: PaginationDep,
    title: str | None = Query(None, description='Название отеля'), 
    location: str| None = Query(None, description='Адрес отеля')
    
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            title = title,
            location = location,
            limit = per_page,
            offset=((pagination.page - 1) * per_page)
        )


 
@router.post('', summary='Добавление нового отеля')
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {"summary": "Сочи", "value": {
        "title": "Отель Сочи 19 звезд",
        "location": "Сочи, ул. Моря 21"
    }},
    "2": {"summary": "Дубай", "value": {
        "title": "Отель дубай 2 звезды",
        "location": "Дубайск, Золото шейха 17"
    }}})
):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()

    return {'status': 'ok', 'data': hotel}


@router.put('/{hotel_id}', summary='Полное обновлление информации об отеле')
async def change_hotel(hotel_id: int, hotel_data: Hotel):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
    return {'status': 'ok'}

        

@router.patch('/{hotel_id}', summary='Частичное обновление данных об отеле', description='Что-то более подробное')
def rewrite_hotel(
    hotel_id: int,
    hotel_data: HotelPatch
):
    global hotels

    hotel = [hotel for hotel in hotels if hotel['id'] == hotel_id][0]
    hotel['title'] = hotel_data.title if hotel_data.title is not None else hotel['title']
    hotel['name'] = hotel_data.name if hotel_data.name is not None else hotel['name']
    return {'status': 'ok'}


@router.delete('/{hotel_id}', summary='Удаление отеля')
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()
    return {'status': 'ok'}