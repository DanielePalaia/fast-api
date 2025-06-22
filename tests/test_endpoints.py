from datetime import datetime, timedelta, timezone
import pytest

from fever_integration import Plan


@pytest.mark.asyncio
async def test_get_events_returns_filtered_events(client, db_session):
    await db_session.execute(Plan.__table__.delete())
    await db_session.commit()

    now = datetime.now(timezone.utc).replace(microsecond=0)

    plan1 = Plan(
        id="1",
        base_plan_id="bp1",
        title="Event One",
        start_datetime=now + timedelta(days=1),
        end_datetime=now + timedelta(days=2),
        last_seen=now,
        min_price=10,
        max_price=20,
    )
    plan2 = Plan(
        id="2",
        base_plan_id="bp2",
        title="Event Two",
        start_datetime=now + timedelta(days=3),
        end_datetime=now + timedelta(days=4),
        last_seen=now,
        min_price=15,
        max_price=25,
    )
    db_session.add_all([plan1, plan2])
    await db_session.commit()

    starts_at = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    ends_at = (now + timedelta(days=10)).isoformat().replace("+00:00", "Z")

    response = await client.get(f"/events?starts_at={starts_at}&ends_at={ends_at}")

    assert response.status_code == 200
    data = response.json()
    events = data.get("data", {}).get("events")

    assert events is not None and len(events) >= 2
    assert any(e["id"] == "bp1" for e in events)
    assert any(e["id"] == "bp2" for e in events)