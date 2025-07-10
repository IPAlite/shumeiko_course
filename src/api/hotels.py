from fastapi import Query, Body, APIRouter

from schemas.hotels import Hotel, HotelAdd,  HotelPatch
from src.api.dependencies import PaginationDep
from src.database import async_session_maker
from src.repositories.hotels import HotelsRepository

router = APIRouter(prefix='/hotels', tags=['Отели'])



@router.get('', summary='Получение информации об отелях')
async def get_hotels(
    pagination: PaginationDep,
    location: str | None = Query(None, description='Место расположения отеля'),
    title: str | None = Query(None, description='Название отеля'), 
    
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            location=location,
            title=title,
            limit=per_page,
            offset=(pagination.page-1) * per_page)


@router.get('/{hotel_id}', summary='Получение информации об отеле по id')
async def get_hotel_by_id(hotel_id: int):
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_one_or_none(id=hotel_id)


@router.post('', summary='Добавление нового отеля')
async def create_hotel(hotel_data: HotelAdd = Body(openapi_examples={
    "1": {"summary": "Сочи", "value": {
        "title": "Отель Сочи 19 звезд",
        "location": "Сочи, ул пездова 19"
    }},
    "2": {"summary": "Дубай", "value": {
        "title": "Отель дубай 2 звезды",
        "location": "Дубайск, ул шлюхи 2"
    }}})
):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {'status': 'ok', 'data': hotel}


@router.put('/{hotel_id}', summary='Полное обновлление информации об отеле')
async def change_hotel(hotel_id: int, hotel_data: HotelAdd):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(data=hotel_data, id=hotel_id, exclude_unset=False)
        await session.commit()
    return {'status': 'ok'}


@router.patch('/{hotel_id}', summary='Частичное обновление данных об отеле', description='Что-то более подробное')
async def rewrite_hotel(
    hotel_id: int,
    hotel_data: HotelPatch
):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(data=hotel_data, id=hotel_id, exclude_unset=True)
        await session.commit()
    return {'status': 'ok'}


@router.delete('/{hotel_id}', summary='Удаление отеля')
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id = hotel_id)
        await session.commit()
    return {'status': 'ok'}