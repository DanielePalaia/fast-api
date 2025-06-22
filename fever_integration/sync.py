import asyncio
import logging
from typing import List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .client import FeverClient
from .models import Plan
from .session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def sync_events() -> None:
    client = FeverClient()
    async with AsyncSessionLocal() as db:
        try:
            plans: List[Plan] = await client.fetch_events()
            for plan in plans:
                stmt = insert(Plan).values(
                    id=plan.id,
                    base_plan_id=plan.base_plan_id,
                    title=plan.title,
                    start_datetime=plan.start_datetime,
                    end_datetime=plan.end_datetime,
                    last_seen=plan.last_seen,
                    min_price=plan.min_price,
                    max_price=plan.max_price,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        "base_plan_id": plan.base_plan_id,
                        "title": plan.title,
                        "start_datetime": plan.start_datetime,
                        "end_datetime": plan.end_datetime,
                        "last_seen": plan.last_seen,
                        "min_price": plan.min_price,
                        "max_price": plan.max_price,
                    },
                )
                await db.execute(stmt)
            await db.commit()
            logger.info(f"Synced {len(plans)} plans successfully.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Sync failed: {str(e)}", exc_info=True)


async def background_sync(refresh_timeout: int) -> None:
    while True:
        await asyncio.sleep(refresh_timeout)
        await sync_events()
