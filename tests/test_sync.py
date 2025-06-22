import pytest
from datetime import datetime, timezone
from fever_integration import FeverClient, Plan, sync_events

@pytest.mark.asyncio
async def test_sync_updates_plan_price(monkeypatch, db_session):
    session = await anext(db_session)

    await session.execute(Plan.__table__.delete().where(Plan.id == "sync2"))
    await session.commit()

    # Insert initial plan
    initial_plan = Plan(
        id="sync2",
        base_plan_id="bp_sync2",
        title="Price Update Event",
        start_datetime=datetime.fromisoformat("2025-01-01T10:00:00"),
        end_datetime=datetime.fromisoformat("2025-01-01T12:00:00"),
        last_seen=datetime.now(timezone.utc),
        min_price=10.0,
        max_price=20.0,
    )
    session.add(initial_plan)
    await session.commit()

    updated_plan = Plan(
        id="sync2",
        base_plan_id="bp_sync2",
        title="Price Update Event",
        start_datetime=datetime.fromisoformat("2025-01-01T10:00:00"),
        end_datetime=datetime.fromisoformat("2025-01-01T12:00:00"),
        last_seen=datetime.now(timezone.utc),
        min_price=12.0,
        max_price=25.0,
    )

    async def mock_fetch_events(self):
        return [updated_plan]

    monkeypatch.setattr(FeverClient, "fetch_events", mock_fetch_events)

    await sync_events()

    result = await session.get(Plan, "sync2")
    assert result.min_price == 12.0
    assert result.max_price == 25.0


@pytest.mark.asyncio
async def test_sync_events_inserts_and_updates(monkeypatch, db_session):
    session = await anext(db_session)

    await session.execute(Plan.__table__.delete())
    await session.commit()

    event1 = Plan(
        id="sync1",
        base_plan_id="bp_sync1",
        title="Sync Test Event",
        start_datetime=datetime.fromisoformat("2025-01-01T10:00:00"),
        end_datetime=datetime.fromisoformat("2025-01-01T12:00:00"),
        last_seen=datetime.now(timezone.utc),
        min_price=10.0,
        max_price=20.0,
    )

    async def mock_fetch_events(self):
        return [event1]

    monkeypatch.setattr(FeverClient, "fetch_events", mock_fetch_events)

    await sync_events()

    result = await session.get(Plan, "sync1")
    assert result.title == "Sync Test Event"

    event1_updated = Plan(
        id="sync1",
        base_plan_id="bp_sync1",
        title="Sync Test Event",
        start_datetime=datetime.fromisoformat("2025-01-01T10:00:00"),
        end_datetime=datetime.fromisoformat("2025-01-01T12:00:00"),
        last_seen=datetime.now(timezone.utc),
        min_price=15.0,
        max_price=25.0,
    )

    monkeypatch.setattr(FeverClient, "fetch_events", lambda self: [event1_updated])

    await sync_events()

    result = await session.get(Plan, "sync1")
    assert result.min_price == 15.0
    assert result.max_price == 25.0