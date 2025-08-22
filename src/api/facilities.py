from fastapi import APIRouter

from src.schemas.facilities import FacilitiesAdd
from src.api.dependencies import DBDep

router = APIRouter(prefix='/facilities', tags=['Удобства'])


@router.get('', summary='Получение всех удобств')
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post('', summary='Добавление удобства')
async def create_facility(facility_data: FacilitiesAdd, db: DBDep):
    facility = await db.facilities.add(facility_data)
    await db.commit()
    return {'status': 'ok', 'data': facility}