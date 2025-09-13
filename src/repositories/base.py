from typing import Sequence

from fastapi import HTTPException 

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError

from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError

from pydantic import BaseModel

from src.exceptions import ObjectAlredyExistsException, ObjectNotFoundException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> BaseModel | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)
    
    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        
        except NoResultFound:
            raise ObjectNotFoundException
        
        except ForeignKeyViolationError:
            raise ObjectNotFoundException

        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        try:
            add_obj_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(add_obj_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlredyExistsException from ex
            else:
                raise ex

    async def add_bulk(self, data: Sequence[BaseModel]):
        if not data:
            return []
        add_obj_stmt = (
            insert(self.model).values([item.model_dump() for item in data]).returning(self.model)
        )
        await self.session.execute(add_obj_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        checker = await self.session.execute(select(self.model).filter_by(**filter_by))
        rows = checker.scalars().all()
        if not rows:
            raise ObjectNotFoundException
        if len(rows) > 1:
            raise HTTPException(status_code=400, detail="More than one object found")
        edit_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(edit_stmt)

    async def delete(self, **filter_by) -> None:
        checker = await self.session.execute(select(self.model).filter_by(**filter_by))
        rows = checker.scalars().all()
        if not rows:
            raise ObjectNotFoundException
        if len(rows) > 1:
            raise HTTPException(status_code=400, detail="More than one object found")
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)

    async def delete_all(self) -> None:
        delete_stmt = delete(self.model)
        await self.session.execute(delete_stmt)
