from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.db import Base  # Изменён импорт


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False)
    clicked_at = Column(DateTime, server_default=func.now())
