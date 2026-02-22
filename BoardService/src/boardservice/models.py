from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Board(Base):
    __tablename__ = "boards"

    id = Column(BigInteger, primary_key=True)
    name  = Column(String, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    amount_of_pins = Column(Integer, default=0)
    cover_url =  Column(String, nullable=True)
    type = Column(Boolean, default=0)
    description = Column(String, default=None)

    pins = relationship("Pins_to_Board", back_populates="board")

class Pins_to_Board(Base):
    __tablename__ = "pins_to_board"

    id = Column(BigInteger, primary_key=True)
    pin_id = Column(BigInteger, nullable=False)
    board_id = Column(BigInteger, ForeignKey("boards.id", ondelete="CASCADE"))

    board = relationship("Board", back_populates="pins")
