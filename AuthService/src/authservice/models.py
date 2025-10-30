from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, Relationship, declarative_base, mapped_column


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(40), nullable = False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique = True, nullable=False)
    role: Mapped[str] = mapped_column(String(24), nullable=False, default="user")

    refresh_token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)