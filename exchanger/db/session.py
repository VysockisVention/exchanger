from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from exchanger.core.config import get_settings

settings = get_settings()

sessionmaker = async_sessionmaker(expire_on_commit=False)


@asynccontextmanager
async def setup_db():
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,  # logs SQL if debug=True
        pool_pre_ping=True,
    )

    sessionmaker.configure(bind=engine)
    yield
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with sessionmaker() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
