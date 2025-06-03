from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from src.db import Base  # Изменён импорт


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_url = Column(String(10), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, default=0)
