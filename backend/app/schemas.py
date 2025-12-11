from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, PlainSerializer


def parse_date(v):
    if isinstance(v, date): return v
    try:
        return datetime.strptime(v, '%d.%m.%Y').date()
    except ValueError:
        raise ValueError("Birthday must be in dd.mm.yyyy format")


def serialize_date(v: date):
    return v.strftime('%d.%m.%Y')


MyDate = Annotated[
    date,
    BeforeValidator(parse_date),
    PlainSerializer(serialize_date, return_type=str)
]


class FriendBase(BaseModel):
    full_name: str
    birthday: MyDate


class FriendCreate(FriendBase):
    pass


class FriendUpdate(BaseModel):
    full_name: str | None = None
    birthday: MyDate | None = None


class Friend(FriendBase):
    id: int

    class Config:
        from_attributes = True


# --- Rule Schemas ---

class RuleBase(BaseModel):
    days_before: int


class RuleCreate(RuleBase):
    pass


class RuleUpdate(RuleBase):
    pass


class Rule(RuleBase):
    id: int

    class Config:
        from_attributes = True


# --- Responses ---

class DeleteResponse(BaseModel):
    status: str
    id: int
