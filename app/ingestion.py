from fastapi import APIRouter

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import Event

router = APIRouter()


@router.post("/events/ingest")
def ingest_events(events: list[dict]):

    db: Session = SessionLocal()

    inserted = 0

    duplicates = 0

    for event in events:

        existing = db.query(Event).filter(
            Event.event_id == event["event_id"]
        ).first()

        if existing:

            duplicates += 1

            continue

        db_event = Event(

            event_id=event.get("event_id"),

            store_id=event.get("store_id"),

            camera_id=event.get("camera_id"),

            visitor_id=event.get("visitor_id"),

            event_type=event.get("event_type"),

            timestamp=event.get("timestamp"),

            zone_id=event.get("zone_id"),

            dwell_ms=event.get("dwell_ms", 0),

            is_staff=event.get("is_staff", False),

            confidence=event.get("confidence", 0.0)
        )

        db.add(db_event)

        inserted += 1

    db.commit()

    db.close()

    return {

        "inserted": inserted,

        "duplicates": duplicates
    }