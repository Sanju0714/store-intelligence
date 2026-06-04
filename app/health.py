from fastapi import APIRouter

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import Event

router = APIRouter()


@router.get("/health")
def health_check():

    db: Session = SessionLocal()

    last_event = db.query(Event).order_by(
        Event.timestamp.desc()
    ).first()

    db.close()

    if last_event:

        return {

            "status": "healthy",

            "last_event_timestamp":
                last_event.timestamp,

            "store_id":
                last_event.store_id
        }

    return {

        "status": "healthy",

        "message":
            "No events received yet"
    }