from sqlalchemy import String, BigInteger, Float, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=True, unique=False)
    phone_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    stars: Mapped[float] = mapped_column(Float, unique=False, default=0)  # Потом поменять !!!
    blocked: Mapped[bool] = mapped_column(Boolean, unique=False, default=False)
