from fastapi import APIRouter

from src.schemas.facilities import FacilitiesAddRequest
from src.api.dependencies import DBDep

router = APIRouter(prefix='/facilities', tags=['Удобства'])


@router.get('', summary='Получение всех удобств')
async def get_all_facility(db: DBDep):
    return await db.facilities.get_all()


@router.post('', summary='Добавление удобства')
async def create_facility(title: FacilitiesAddRequest, db: DBDep):
    facility = await db.facilities.add(title)
    await db.commit()
    return {'status': 'ok', 'data': facility}