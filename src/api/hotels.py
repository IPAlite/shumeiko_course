from fastapi import Query, Body, APIRouter

from sqlalchemy import insert, select, func

from schemas.hotels import Hotel, HotelPatch
from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsOrm


router = APIRouter(prefix='/hotels', tags=['Отели'])



@router.get('', summary='Получение информации об отелях')
async def get_hotels(
    pagination: PaginationDep,
    title: str | None = Query(None, description='Название отеля'), 
    location: str| None = Query(None, description='Адрес отеля')
    
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        query = select(HotelsOrm)
        if title:
            query = query.filter(func.lower(HotelsOrm.title).like(f"%{title.strip().lower()}%"))
        if location:
            query = query.filter(func.lower(HotelsOrm.location).like(f"%{location.strip().lower()}%"))
        query = (
            query
            .limit(per_page)
            .offset((pagination.page - 1) * per_page)
        )
        print(query.compile(compile_kwargs={"literal_binds":True}))
        result = await session.execute(query) 
        hotels = result.scalars().all()

        return hotels

 
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
        add_hotel_stmt = insert(HotelsOrm).values(**hotel_data.model_dump())
        ## DEBUG STRING
        print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds": True }))
        await session.execute(add_hotel_stmt)
        await session.commit()

    
    return {'status': 'ok'}


@router.put('/{hotel_id}', summary='Полное обновлление информации об отеле')
def change_hotel(hotel_id: int, hotel_data: Hotel):
    global hotels

    hotel = [hotel for hotel in hotels if hotel['id'] == hotel_id][0]
    hotel['title'] = hotel_data.title
    hotel['name'] = hotel_data.name
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
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel['id'] != hotel_id ]
    return {'status': 'ok'}