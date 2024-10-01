from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from database import User, async_session_maker
from auth.base_config import auth_backend, fastapi_users
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
from operations.router import router as router_operation
from tasks.router import router as router_report


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Trading App",
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


# @app.on_event("startup")
# async def startup():
#     session = async_session_maker()
#     try:
#         # Заполняем таблицу 'operation' тестовыми данными
#         test_data = [
#             {
#                 'quantity': '100',
#                 'figi': 'BBG000BPH474',
#                 'instrument_type': 'stock',
#                 'date': '2023-10-26',
#                 'type': 'buy',
#             },
#             {
#                 'quantity': '50',
#                 'figi': 'BBG000BPH475',
#                 'instrument_type': 'bond',
#                 'date': '2023-10-27',
#                 'type': 'sell',
#             },
#             # Добавьте сюда больше тестовых данных...
#         ]
#
#         # Вставка данных в таблицу
#         for data in test_data:
#             await session.execute(
#                 text(
#                     "INSERT INTO operation (quantity, figi, instrument_type, date, type) VALUES (:quantity, :figi, :instrument_type, :date, :type)"),
#                 data
#             )
#         await session.commit()
#
#         print("Тестовые данные успешно добавлены в таблицу 'operation'.")
#     finally:
#         await session.close()


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(router_operation)
app.include_router(router_report)
