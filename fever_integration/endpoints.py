from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Plan
from .session import get_db

router = APIRouter()

@router.get("/events")
async def get_events(
    starts_at: str = Query(
        ...,
        description="Filter events starting at or after this datetime (ISO8601, e.g. 2021-07-21T17:32:28Z)",
        example="2021-07-21T17:32:28Z",
    ),
    ends_at: str = Query(
        ...,
        description="Filter events ending at or before this datetime (ISO8601, e.g. 2021-07-21T17:32:28Z)",
        example="2021-07-21T17:32:28Z",
    ),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        starts_at_dt = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
        ends_at_dt = datetime.fromisoformat(ends_at.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid datetime format. Use ISO8601 with 'Z' timezone.",
        )

    starts_at_dt = starts_at_dt.replace(tzinfo=None)
    ends_at_dt = ends_at_dt.replace(tzinfo=None)

    stmt = (
        select(
            Plan.base_plan_id,
            Plan.title,
            func.min(Plan.start_datetime).label("start_datetime"),
            func.max(Plan.end_datetime).label("end_datetime"),
            func.min(Plan.min_price).label("min_price"),
            func.max(Plan.max_price).label("max_price"),
        )
        .where(
            Plan.start_datetime >= starts_at_dt,
            Plan.end_datetime <= ends_at_dt,
        )
        .group_by(Plan.base_plan_id, Plan.title)
    )

    result = await db.execute(stmt)
    aggregated_plans = result.all()

    response_events = []
    for plan in aggregated_plans:
        response_events.append(
            {
                "id": plan.base_plan_id,
                "title": plan.title,
                "start_date": plan.start_datetime.date().isoformat(),
                "start_time": plan.start_datetime.time().isoformat(),
                "end_date": plan.end_datetime.date().isoformat(),
                "end_time": plan.end_datetime.time().isoformat(),
                "min_price": plan.min_price,
                "max_price": plan.max_price,
            }
        )

    return {"data": {"events": response_events}, "error": None}