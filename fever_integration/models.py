from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String, primary_key=True)  # unique plan id (composite string)
    base_plan_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=False, index=True)
    last_seen = Column(DateTime, nullable=False)
    min_price = Column(Float, nullable=False, default=0.0)
    max_price = Column(Float, nullable=False, default=0.0)
