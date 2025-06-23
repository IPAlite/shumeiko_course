from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from schemas.hotels import Hotel


from sqlalchemy import select, insert, func


class HotelsRepository(BaseRepository):
    model = HotelsOrm

    async def get_all(self, title, location, limit, offset):
        query = select(HotelsOrm)
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        print(query.compile(compile_kwargs={"literal_binds":True}))
        result = await self.session.execute(query) 
        
        return result.scalars().all()
    