import json
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs:lambda f: f).start()

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.database import Base, engine_null_pool
from src.database import async_session_maker_null_pool
from src.api.dependencies import get_db
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBmanager
from src.models import *
from src.main import app


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBmanager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope='function')
async def db() -> DBmanager:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope='session', autouse=True)
async def replenishment_of_the_database(setup_database):
    with open('tests/mock_hotels.json', 'r', encoding='utf-8') as file_hotels:
        hotels_data = json.load(file_hotels)
    with open('tests/mock_rooms.json', 'r', encoding='utf-8') as file_rooms:
        rooms_data = json.load(file_rooms)

    holels = [HotelAdd.model_validate(hotel) for hotel in hotels_data]
    rooms = [RoomAdd.model_validate(room) for room in rooms_data]

    async with DBmanager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(holels)
        await db_.rooms.add_bulk(rooms)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
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
        

@pytest.fixture(scope='session', autouse=True)
async def authenticated_ac(register_user, ac):
    response = await ac.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "string"
        }
    )
    assert response.status_code == 200
    assert ac.cookies
    yield ac


    