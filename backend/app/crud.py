from typing import Sequence

from sqlalchemy import extract, select
from sqlalchemy.orm import Session

from . import models, schemas
from .exceptions import DuplicateRuleError, RuleNotFoundError
from .models import Friend, NotificationRule


def get_friends_with_birthday_on_day(db: Session, month: int, day: int):
    stmt = select(models.Friend).where(
        extract('month', models.Friend.birthday) == month,
        extract('day', models.Friend.birthday) == day
    )
    return db.execute(stmt).scalars().all()


# GET
def get_friend(db: Session, friend_id: int) -> models.Friend | None:
    return db.execute(select(models.Friend).where(models.Friend.id == friend_id)).scalar_one_or_none()


def get_friends(db: Session, skip: int = 0, limit: int = 100):
    stmt = select(models.Friend).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


# CREATE
def create_friend(db: Session, friend: schemas.FriendCreate) -> Friend:
    # Convert Pydantic model to SQLAlchemy model
    db_friend = models.Friend(full_name=friend.full_name, birthday=friend.birthday)
    db.add(db_friend)
    db.commit()
    db.refresh(db_friend)  # Refresh to get the new ID
    return db_friend


# UPDATE
def update_friend(db: Session, friend_id: int, friend_update: schemas.FriendUpdate) -> models.Friend | None:
    db_friend = get_friend(db, friend_id)
    if not db_friend:
        return None

    update_data = friend_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_friend, key, value)

    db.commit()
    db.refresh(db_friend)

    return db_friend


# DELETE
def delete_friend(db: Session, friend_id: int) -> Friend | None:
    db_friend = get_friend(db, friend_id)
    if db_friend:
        db.delete(db_friend)
        db.commit()
    return db_friend


# --- Rule Operations ---
# GET
def get_rules(db: Session):
    return db.execute(select(models.NotificationRule)).scalars().all()


def get_rule(db: Session, rule_id: int) -> models.NotificationRule | None:
    return db.execute(
        select(models.NotificationRule).where(models.NotificationRule.id == rule_id)
    ).scalar_one_or_none()


def get_rules_by_hour(db: Session, hour: int) -> Sequence[models.NotificationRule]:
    statement = select(models.NotificationRule).where(models.NotificationRule.hour == hour)
    return db.execute(statement).scalars().all()


def get_rule_by_days_before(db: Session, days_before: int) -> models.NotificationRule:
    statement = select(models.NotificationRule).where(models.NotificationRule.days_before == days_before)
    return db.execute(statement).scalar_one_or_none()


# CREATE
def create_rule(db: Session, rule: schemas.RuleCreate) -> models.NotificationRule:
    # Check for existing rule with same days_before
    existing = db.execute(
        select(models.NotificationRule).where(models.NotificationRule.days_before == rule.days_before)
    ).scalar_one_or_none()

    if existing:
        raise DuplicateRuleError(f"Rule with days_before={rule.days_before} already exists")

    db_rule = models.NotificationRule(days_before=rule.days_before, hour=rule.hour)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


# UPDATE
def update_rule(db: Session, rule_id: int, rule_update: schemas.RuleUpdate) -> NotificationRule:
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        raise RuleNotFoundError(f"Rule with id {rule_id} not found")

    update_data = rule_update.model_dump(exclude_unset=True)

    if "days_before" in update_data:
        existing = get_rule_by_days_before(db, update_data["days_before"])
        if existing and existing.id != rule_id:
            raise DuplicateRuleError("Rule already exists")

    for key, value in update_data.items():
        setattr(db_rule, key, value)

    db.commit()
    db.refresh(db_rule)

    return db_rule


# DELETE
def delete_rule(db: Session, rule_id: int) -> None:
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        raise RuleNotFoundError(f"Rule with id {rule_id} not found")
    db.delete(db_rule)
    db.commit()
