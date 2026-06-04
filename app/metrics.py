from fastapi import APIRouter

from sqlalchemy.orm import Session

from sqlalchemy import func

from app.database import SessionLocal

from app.models import Event

router = APIRouter()


# ==========================================
# TOTAL METRICS
# ==========================================
@router.get("/metrics/summary")
def metrics_summary():

    db: Session = SessionLocal()

    entry_count = db.query(Event).filter(
        Event.event_type == "ENTRY"
    ).count()

    exit_count = db.query(Event).filter(
        Event.event_type == "EXIT"
    ).count()

    reentry_count = db.query(Event).filter(
        Event.event_type == "REENTRY"
    ).count()

    occupancy = max(
        0,
        entry_count - exit_count
    )

    return {

        "entry_count": entry_count,

        "exit_count": exit_count,

        "reentry_count": reentry_count,

        "occupancy": occupancy
    }


# ==========================================
# ZONE ANALYTICS
# ==========================================
@router.get("/metrics/zones")
def zone_metrics():

    db: Session = SessionLocal()

    results = db.query(

        Event.zone_id,

        func.count(Event.event_id)

    ).group_by(
        Event.zone_id
    ).all()

    zone_data = {}

    for zone_id, count in results:

        if zone_id:

            zone_data[zone_id] = count

    return zone_data


# ==========================================
# BILLING ANALYTICS
# ==========================================
@router.get("/metrics/billing")
def billing_metrics():

    db: Session = SessionLocal()

    queue_events = db.query(Event).filter(
        Event.event_type == "BILLING_QUEUE_JOIN"
    ).count()

    return {

        "billing_queue_events": queue_events
    }


# ==========================================
# STAFF ANALYTICS
# ==========================================
@router.get("/metrics/staff")
def staff_metrics():

    db: Session = SessionLocal()

    staff_events = db.query(Event).filter(
        Event.is_staff == True
    ).count()

    return {

        "staff_events": staff_events
    }
