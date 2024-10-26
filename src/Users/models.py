from sqlalchemy import Column, String, Integer, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    avatar = Column(LargeBinary)
    gender = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    longitude = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
