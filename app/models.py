from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import Integer

from app.database import Base


class Event(Base):

    __tablename__ = "events"

    event_id = Column(
        String,
        primary_key=True,
        index=True
    )

    store_id = Column(String)

    camera_id = Column(String)

    visitor_id = Column(String)

    event_type = Column(String)

    timestamp = Column(String)

    zone_id = Column(String)

    dwell_ms = Column(Integer)

    is_staff = Column(Boolean)

    confidence = Column(Float)