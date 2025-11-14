from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Comment(Base):
    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    pin_id = Column(BigInteger, nullable=False)
    text = Column(Text, default="")
    likes = Column(Integer, default=0)
    reply_to = Column(BigInteger, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    amount_of_replies = Column(Integer, default=0)
