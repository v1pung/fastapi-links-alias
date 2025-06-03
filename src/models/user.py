from sqlalchemy import Column, Integer, String
from src.db import Base  # Изменён импорт


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
