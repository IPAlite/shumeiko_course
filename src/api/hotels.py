from fastapi import Query, Body, APIRouter
from schemas.hotels import Hotel, HotelPatch
from src.api.dependencies import PaginationDep


router = APIRouter(prefix='/hotels', tags=['Отели'])

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldivi"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]


@router.get('', summary='Получение информации об отелях')
def get_hotels(
    pagination: PaginationDep,
    id: int | None = Query(None, description='ID отеля'),
    title: str | None = Query(None, description='Название отеля'), 
    
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel['id'] != id:
            continue
        if title and hotel['title'] != title:
            continue
        hotels_.append(hotel)
    
    if pagination.page and pagination.per_page:
        return hotels_[(pagination.page-1) * pagination.per_page:] [:pagination.per_page]
    return hotels_

 
@router.post('', summary='Добавление нового отеля')
def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {"summary": "Сочи", "value": {
        "title": "Отель Сочи 19 звезд",
        "name": "Сочи 19"
    }},
    "2": {"summary": "Дубай", "value": {
        "title": "Отель дубай 2 звезды",
        "name": "Дубайск"
    }}})
):
    global hotels
    hotels.append(
        {
            "id": len(hotels) + 1,
            "title": hotel_data.title,
            "name": hotel_data.name
        }
    )
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