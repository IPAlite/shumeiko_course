from fastapi import HTTPException

from sqlalchemy import select, insert

from pydantic import BaseModel

from repositories.mappers.mappers import UserDataMapper
from src.repositories.base import BaseRepository
from src.models.users import UserOrm
from src.schemas.users import User


class UserRepository(BaseRepository):
    model = UserOrm
    mapper = UserDataMapper

    async def add(self, data: BaseModel):
        query = select(self.model).where(self.model.email == data.email)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()

        if model:
            raise HTTPException(status_code=409, detail='Пользователь с таким email существует!')
        
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_stmt)
        model = result.scalars().one()
        return UserDataMapper.map_to_domain_entity(model)
