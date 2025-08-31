import json

from fastapi import APIRouter

from src.init import redis_manager

from src.schemas.facilities import FacilitiesAdd
from src.api.dependencies import DBDep

router = APIRouter(prefix='/facilities', tags=['Удобства'])


@router.get('', summary='Получение всех удобств')
async def get_facilities(db: DBDep):
    facilities_from_cache = await redis_manager.get("facilities")
    print (f"{facilities_from_cache=}")
    if not facilities_from_cache:
        facilities = await db.facilities.get_all()
        facilities_schemas: list[dict] = [f.model_dump() for f in facilities]
        facilities_json = json.dumps(facilities_schemas)
        await redis_manager.set("facilities", facilities_json, expire=10)
        return facilities
    else:
        facilities_dicts = json.loads(facilities_from_cache)
        return facilities_dicts


@router.post('', summary='Добавление удобства')
async def create_facility(facility_data: FacilitiesAdd, db: DBDep):
    facility = await db.facilities.add(facility_data)
    await db.commit()
    return {'status': 'ok', 'data': facility}