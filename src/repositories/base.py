from fastapi import HTTPException

from sqlalchemy import select, insert, update, delete

from pydantic import BaseModel

class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query) 

        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query) 

        return result.scalars().one_or_none()
    
    
    async def add(self, data: BaseModel):
        add_obj_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_obj_stmt)
        return result.scalars().one()
    
    async def edit(self, data: BaseModel, exclude_unset: bool = False,  **filter_by) -> None:
        checker = await self.session.execute(select(self.model).filter_by(**filter_by))
        rows = checker.scalars().all()
        if not rows:
            raise HTTPException(status_code=404, detail="Object not found")
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
            raise HTTPException(status_code=404, detail="Object not found")
        if len(rows) > 1:
            raise HTTPException(status_code=400, detail="More than one object found")
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)