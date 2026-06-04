from fastapi import APIRouter

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import Event

router = APIRouter()


@router.get("/stores/{store_id}/funnel")
def get_funnel(
    store_id: str
):

    db: Session = SessionLocal()

    events = db.query(Event).filter(
        Event.store_id == store_id
    ).all()

    db.close()

    # ==========================================
    # UNIQUE VISITORS
    # ==========================================
    entries = set()

    zone_visits = set()

    billing_visits = set()

    purchases = set()

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

            entries.add(
                event.visitor_id
            )

        elif event.event_type in [
            "ZONE_ENTER",
            "ZONE_DWELL"
        ]:

            zone_visits.add(
                event.visitor_id
            )

        elif event.event_type == (
            "BILLING_QUEUE_JOIN"
        ):

            billing_visits.add(
                event.visitor_id
            )

        elif event.event_type == (
            "PURCHASE"
        ):

            purchases.add(
                event.visitor_id
            )

    # ==========================================
    # COUNTS
    # ==========================================
    entry_count = len(entries)

    zone_count = len(zone_visits)

    billing_count = len(
        billing_visits
    )

    purchase_count = len(
        purchases
    )

    # ==========================================
    # DROP OFF %
    # ==========================================
    zone_dropoff = 0

    billing_dropoff = 0

    purchase_dropoff = 0

    if entry_count > 0:

        zone_dropoff = round(

            (
                (
                    entry_count -
                    zone_count
                )
                / entry_count
            ) * 100,
            2
        )

    if zone_count > 0:

        billing_dropoff = round(

            (
                (
                    zone_count -
                    billing_count
                )
                / zone_count
            ) * 100,
            2
        )

    if billing_count > 0:

        purchase_dropoff = round(

            (
                (
                    billing_count -
                    purchase_count
                )
                / billing_count
            ) * 100,
            2
        )

    return {

        "store_id": store_id,

        "funnel": {

            "entry": entry_count,

            "zone_visit": zone_count,

            "billing_queue":
                billing_count,

            "purchase":
                purchase_count
        },

        "dropoff_percent": {

            "entry_to_zone":
                zone_dropoff,

            "zone_to_billing":
                billing_dropoff,

            "billing_to_purchase":
                purchase_dropoff
        }
    }