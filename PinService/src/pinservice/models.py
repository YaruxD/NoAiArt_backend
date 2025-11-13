from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Pin(Base):
    __tablename__ = "pins"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    image_url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    cost = Column(Integer, default=0)
