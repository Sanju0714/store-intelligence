from fastapi import APIRouter

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import Event

router = APIRouter()


@router.get("/stores/{store_id}/anomalies")
def get_anomalies(
    store_id: str
):

    db: Session = SessionLocal()

    events = db.query(Event).filter(
        Event.store_id == store_id
    ).all()

    db.close()

    anomalies = []

    # ==========================================
    # COUNTS
    # ==========================================
    entries = 0

    billing_queue = 0

    purchases = 0

    zone_events = 0

    # ==========================================
    # PROCESS EVENTS
    # ==========================================
    for event in events:

        if event.is_staff:
            continue

        if event.event_type in [
            "ENTRY",
            "REENTRY"
        ]:

            entries += 1

        elif event.event_type == (
            "BILLING_QUEUE_JOIN"
        ):

            billing_queue += 1

        elif event.event_type == (
            "PURCHASE"
        ):

            purchases += 1

        elif event.event_type in [
            "ZONE_ENTER",
            "ZONE_DWELL"
        ]:

            zone_events += 1

    # ==========================================
    # QUEUE SPIKE
    # ==========================================
    if billing_queue >= 10:

        anomalies.append({

            "type":
                "QUEUE_SPIKE",

            "severity":
                "CRITICAL",

            "message":
                "Billing queue unusually high",

            "suggested_action":
                "Open additional billing counter"
        })

    # ==========================================
    # LOW CONVERSION
    # ==========================================
    conversion_rate = 0

    if entries > 0:

        conversion_rate = (
            purchases / entries
        ) * 100

    if (
        entries > 5
        and conversion_rate < 20
    ):

        anomalies.append({

            "type":
                "LOW_CONVERSION",

            "severity":
                "WARN",

            "message":
                "Store conversion rate dropped",

            "suggested_action":
                "Check customer engagement"
        })

    # ==========================================
    # DEAD ZONE
    # ==========================================
    if zone_events == 0:

        anomalies.append({

            "type":
                "DEAD_ZONE",

            "severity":
                "INFO",

            "message":
                "No recent zone activity",

            "suggested_action":
                "Verify camera coverage"
        })

    return {

        "store_id": store_id,

        "active_anomalies":
            anomalies,

        "total_anomalies":
            len(anomalies)
    }