import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from .config import settings
from .endpoints import router
from .models import Base
from .session import engine
from .sync import background_sync, sync_events
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # create tables asynchronously
    await create_tables(engine)

    # run initial sync (ensure sync_events is async and awaited)
    await sync_events()

    # launch background sync task
    asyncio.create_task(background_sync(settings.REFRESH_TIMEOUT))

    yield


app = FastAPI(
    title="Fever Events API",
    description="API to fetch and sync events with min/max prices and availability status.",
    version="1.0.0",
    contact={"name": "Daniele", "email": "daniele985@gmail.com"},
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
)

app.include_router(router)

if __name__ == "__main__":

    uvicorn.run(
        "fever_integration.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
