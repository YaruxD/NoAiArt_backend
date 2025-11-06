from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger, Date, Boolean
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    posts = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    followed = Column(Integer, default=0)
    avatar_url = Column(String, nullable=True)
    card_image1 = Column(String, nullable=True)
    card_image2 = Column(String, nullable=True)
    collections = Column(Integer, default=0)
    verificated = Column(Boolean, default=False)
    vector_of_interest = Column(Vector(512), nullable=True)
    self_vector = Column(Vector(512), nullable=True)
    description = Column(String, nullable=True)
    Trust = Column(Integer, default=100)
    created_at = Column(Date, nullable=False, default=datetime.now(timezone.utc))

    