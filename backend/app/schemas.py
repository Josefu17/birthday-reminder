from pydantic import BaseModel, field_validator, ConfigDict

from app.utils import MyDate, validate_hour


class FriendBase(BaseModel):
    full_name: str
    birthday: MyDate

    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "Max Mustermensch",
                "birthday": "23.12.1999"
            }
        }
    }


class FriendCreate(FriendBase):
    pass


class FriendUpdate(BaseModel):
    full_name: str | None = None
    birthday: MyDate | None = None


class Friend(FriendBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Rule Schemas ---

class RuleBase(BaseModel):
    days_before: int
    hour: int = 10  # Default to 10 AM

    @field_validator('hour')
    @classmethod
    def check_hour(cls, v):
        return validate_hour(v)

    model_config = {
        "json_schema_extra": {
            "example": {
                "days_before": 7,
                "hour": 9,
            }
        }
    }


class RuleCreate(RuleBase):
    pass


class RuleUpdate(RuleBase):
    # Both optional so we can patch just one field
    days_before: int | None = None
    hour: int | None = None

    @field_validator('hour')
    @classmethod
    def check_hour(cls, v):
        return validate_hour(v)


class Rule(RuleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Responses ---

class DeleteResponse(BaseModel):
    status: str
    id: int
