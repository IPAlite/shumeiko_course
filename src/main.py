from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import uvicorn
import asyncpg

sys.path.append(str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.DEBUG)

from src.init import redis_manager
from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.images import router as router_images


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("FastAPI cache initialize")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_facilities)
app.include_router(router_bookings)
app.include_router(router_images)


@app.exception_handler(DBAPIError)
async def sqlalchemy_exception_handler(request, exc: DBAPIError):
    if isinstance(exc.orig, asyncpg.exceptions.DataError):
        detail = f"Database error: {exc.orig}"
    else:
        detail = f"SQLAlchemy error: {exc}"

    print(f"SQL: {exc.statement}")
    print(f"Parameters: {exc.params}")
    print(f"Error: {exc.orig}")

    return JSONResponse(status_code=400, content={"detail": detail})


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
