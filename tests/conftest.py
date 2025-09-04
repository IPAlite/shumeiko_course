import json

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.database import Base, engine_null_pool
from src.database import async_session_maker_null_pool
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBmanager
from src.models import *
from src.main import app


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope='session', autouse=True)
async def replenishment_of_the_database(setup_database):
    async with DBmanager(session_factory=async_session_maker_null_pool) as db:
        with open('tests/mock_hotels.json', 'r', encoding='utf-8') as hotels_data:
            for hotel in json.loads(hotels_data.read()):
                hotel_data = HotelAdd(**hotel)
                await db.hotels.add(hotel_data)

        with open('tests/mock_rooms.json', 'r', encoding='utf-8') as rooms_data:
            for room in json.loads(rooms_data.read()):
                room_data = RoomAdd(**room)
                await db.rooms.add(room_data)

        await db.commit()


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/auth/register",
            json={
                "first_name": "Гусь",
                "last_name": "Уткович",
                "nikname": "AlonMneVlom",
                "phone": "8800553535",
                "email": "user@example.com",
                "password": "string"
                }   
            )