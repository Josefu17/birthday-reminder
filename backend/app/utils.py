from datetime import date, datetime
from typing import Any, Annotated

from pydantic import BeforeValidator, PlainSerializer


def validate_hour(v: Any) -> Any:
    """Centralized hour validation logic."""
    if v is not None and not (0 <= v <= 23):
        raise ValueError("Hour must be between 0 and 23")
    return v


def parse_date(v: Any):
    if isinstance(v, date): return v
    if isinstance(v, str):
        try:
            return datetime.strptime(v, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Date must be in dd.mm.yyyy format")
    return v


def serialize_date(v: date):
    return v.strftime('%d.%m.%Y')


MyDate = Annotated[
    date,
    BeforeValidator(parse_date),
    PlainSerializer(serialize_date, return_type=str)
]
