from datetime import date

from fastapi import Query, Body, APIRouter, HTTPException
from fastapi_cache.decorator import cache

from src.exceptions import DateErrorException, HotelNotFoundHTTPException, ObjectNotFoundException
from schemas.hotels import HotelAdd, HotelPatch
from src.api.dependencies import PaginationDep, DBDep

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", summary="Получение информации об отелях")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    location: str | None = Query(None, description="Место расположения отеля"),
    title: str | None = Query(None, description="Название отеля"),
    date_from: date = Query(example="2025-08-01"),
    date_to: date = Query(example="2025-08-10"),
):

    per_page = pagination.per_page or 5
    try:
        hotel_resp = await db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            limit=per_page,
            offset=(pagination.page - 1) * per_page,
            location=location,
            title=title,
        )
    except DateErrorException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)
    
    return {"status": "ok", "data": hotel_resp}


@router.get("/{hotel_id}", summary="Получение информации об отеле по id")
@cache(expire=10)
async def get_hotel_by_id(hotel_id: int, db: DBDep):
    try:
        hotel_resp = await db.hotels.get_one(id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    
    return {"status": "ok", "data": hotel_resp}


@router.post("", summary="Добавление нового отеля")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "Отель Сочи 19 звезд",
                    "location": "Сочи, ул пездова 19",
                },
            },
            "2": {
                "summary": "Дубай",
                "value": {
                    "title": "Отель дубай 2 звезды",
                    "location": "Дубайск, ул шлюхи 2",
                },
            },
        }
    ),
):
    hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "ok", "data": hotel}


@router.put("/{hotel_id}", summary="Полное обновлление информации об отеле")
async def change_hotel(hotel_id: int, hotel_data: HotelAdd, db: DBDep):
    await db.hotels.edit(data=hotel_data, id=hotel_id, exclude_unset=False)
    await db.commit()
    return {"status": "ok"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="Что-то более подробное",
)
async def rewrite_hotel(hotel_id: int, hotel_data: HotelPatch, db: DBDep):
    await db.hotels.edit(data=hotel_data, id=hotel_id, exclude_unset=True)
    await db.commit()
    return {"status": "ok"}


@router.delete("/{hotel_id}", summary="Удаление отеля")
async def delete_hotel(hotel_id: int, db: DBDep):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "ok"}
