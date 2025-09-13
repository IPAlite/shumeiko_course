from sqlalchemy import select, insert

from pydantic import BaseModel

from src.exceptions import UserAlredyExistsException
from src.repositories.mappers.mappers import UserDataMapper
from src.repositories.base import BaseRepository
from src.models.users import UserOrm


class UserRepository(BaseRepository):
    model = UserOrm
    mapper = UserDataMapper

    async def add(self, data: BaseModel):
        query = select(self.model).where(self.model.email == data.email)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()

        if model:
            raise UserAlredyExistsException

        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_stmt)
        model = result.scalars().one()
        return UserDataMapper.map_to_domain_entity(model)
