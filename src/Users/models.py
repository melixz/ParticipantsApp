from sqlalchemy import Column, String, Integer, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    avatar = Column(String, nullable=True)
    gender = Column(String(length=10), nullable=False)
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=50), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
