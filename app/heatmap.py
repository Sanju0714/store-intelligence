from fastapi import APIRouter

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models import Event

router = APIRouter()


@router.get("/stores/{store_id}/heatmap")
def get_heatmap(
    store_id: str
):

    db: Session = SessionLocal()

    events = db.query(Event).filter(
        Event.store_id == store_id
    ).all()

    db.close()

    zone_stats = {}

    total_sessions = set()

    # ==========================================
    # PROCESS EVENTS
    # ==========================================
    for event in events:

        if event.is_staff:
            continue

        total_sessions.add(
            event.visitor_id
        )

        if not event.zone_id:
            continue

        zone = event.zone_id

        if zone not in zone_stats:

            zone_stats[zone] = {

                "visit_count": 0,

                "total_dwell_ms": 0
            }

        if event.event_type in [

            "ZONE_ENTER",

            "ZONE_DWELL"
        ]:

            zone_stats[zone][
                "visit_count"
            ] += 1

            zone_stats[zone][
                "total_dwell_ms"
            ] += event.dwell_ms

    # ==========================================
    # NORMALISE
    # ==========================================
    max_visits = 1

    for zone in zone_stats.values():

        max_visits = max(
            max_visits,
            zone["visit_count"]
        )

    heatmap = {}

    for zone_name, data in zone_stats.items():

        avg_dwell = 0

        if data["visit_count"] > 0:

            avg_dwell = round(

                data["total_dwell_ms"]
                / data["visit_count"]
                / 1000,

                2
            )

        intensity = round(

            (
                data["visit_count"]
                / max_visits
            ) * 100,

            2
        )

        heatmap[zone_name] = {

            "visit_count":
                data["visit_count"],

            "avg_dwell_seconds":
                avg_dwell,

            "heat_intensity":
                intensity
        }

    return {

        "store_id": store_id,

        "zones": heatmap,

        "data_confidence":

            "LOW"
            if len(total_sessions) < 20
            else "HIGH"
    }