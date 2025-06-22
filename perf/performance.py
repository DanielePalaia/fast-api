import time
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from fever_integration import Plan, SessionLocal, app


def bulk_insert_plans(db_session, total_plans=100_000):
    base_datetime = datetime(2025, 1, 1, tzinfo=timezone.utc)
    bulk_plans = []

    for i in range(total_plans):
        plan = Plan(
            id=f"perf_{i}",
            base_plan_id=f"bp_perf_{i // 10}",
            title=f"Performance Event {i // 10}",
            start_datetime=base_datetime + timedelta(minutes=i),
            end_datetime=base_datetime + timedelta(minutes=i + 30),
            last_seen=datetime.now(timezone.utc),
            min_price=10.0 + (i % 50),
            max_price=20.0 + (i % 50),
        )
        bulk_plans.append(plan)
        if len(bulk_plans) == 10_000:
            db_session.bulk_save_objects(bulk_plans)
            db_session.commit()
            bulk_plans = []

    if bulk_plans:
        db_session.bulk_save_objects(bulk_plans)
        db_session.commit()


def main():
    db = SessionLocal()

    # Clear existing data
    # db.query(Plan).delete()
    # db.commit()

    print("Inserting plans, please wait...")
    bulk_insert_plans(db, total_plans=100_000)

    client = TestClient(app)

    starts_at = (
        datetime(2025, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    )
    ends_at = (
        (datetime(2026, 1, 1, tzinfo=timezone.utc)).isoformat().replace("+00:00", "Z")
    )

    print("Sending request to /events endpoint...")
    start_time = time.perf_counter()
    response = client.get(f"/events?starts_at={starts_at}&ends_at={ends_at}")
    duration = time.perf_counter() - start_time

    print(f"Response status code: {response.status_code}")
    print(f"Response time: {duration:.2f} seconds")

    if response.status_code == 200:
        data = response.json()
        events = data.get("data", {}).get("events")
        print(f"Number of events returned: {len(events) if events else 0}")

    assert duration < 1.0, "Performance test failed: response took too long"

    # Cleanup
    db.query(Plan).delete()
    db.commit()
    db.close()


if __name__ == "__main__":
    main()
