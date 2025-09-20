from fastapi import APIRouter
from fastapi_cache.decorator import cache

from src.services.facilities import FacilitiesService
from src.api.dependencies import DBDep
from src.schemas.facilities import FacilitiesAdd


router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("", summary="Получение всех удобств")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post("", summary="Добавление удобства")
async def create_facility(facility_data: FacilitiesAdd, db: DBDep):
    facility = await FacilitiesService(db).create_facility(facility_data)
    return {"status": "ok", "data": facility}
