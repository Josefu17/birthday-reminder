from sqlalchemy import Column, Integer, String, Date

from .database import Base


class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    birthday = Column(Date)  # holds year, month and day


class NotificationRule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)

    # unique, so that same day rule isn't persisted twice
    days_before = Column(Integer, unique=True)  # 0 = same day, 1 = one day ago

# TODO make rule also contain the hour info (hour of the day), yb