from src.services.base import BaseService


class FacilitiesService(BaseService):
    async def create_facility(self, facility_data):
        facility = await self.db.facilities.add(facility_data)
        await self.db.commit()

        return facility
