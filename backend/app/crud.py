from sqlalchemy import extract
from sqlalchemy.orm import Session

from . import models, schemas
from .exceptions import DuplicateRuleError, RuleNotFoundError
from .models import Friend, NotificationRule


def get_friends_with_birthday_on_day(db: Session, month: int, day: int):
    """
    Finds friends whose birthday month and day match the arguments.
    """
    return db.query(models.Friend).filter(
        extract('month', models.Friend.birthday) == month,
        extract('day', models.Friend.birthday) == day
    ).all()


# GET
def get_friend(db: Session, friend_id: int) -> models.Friend | None:
    return db.query(models.Friend).filter(models.Friend.id == friend_id).first()


def get_friends(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Friend).offset(skip).limit(limit).all()


# CREATE
def create_friend(db: Session, friend: schemas.FriendCreate) -> Friend:
    # Convert Pydantic model to SQLAlchemy model
    db_friend = models.Friend(
        full_name=friend.full_name,
        birthday=friend.birthday
    )
    db.add(db_friend)
    db.commit()

    db.refresh(db_friend)  # Refresh to get the new ID
    return db_friend


# UPDATE
def update_friend(db: Session, friend_id: int, friend_update: schemas.FriendUpdate) -> models.Friend | None:
    db_friend = get_friend(db, friend_id)

    if not db_friend:
        return None

    if friend_update.full_name:
        db_friend.full_name = friend_update.full_name
    if friend_update.birthday:
        db_friend.birthday = friend_update.birthday

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
    return db.query(models.NotificationRule).all()


def get_rule(db: Session, rule_id: int) -> models.NotificationRule | None:
    return db.query(models.NotificationRule).filter(models.NotificationRule.id == rule_id).first()


# CREATE
def create_rule(db: Session, rule: schemas.RuleCreate) -> models.NotificationRule:
    # Check for existing rule with same days_before
    existing_rule = db.query(models.NotificationRule).filter(
        models.NotificationRule.days_before == rule.days_before
    ).first()

    if existing_rule:
        raise DuplicateRuleError(f"Rule with days_before={rule.days_before} already exists")

    db_rule = models.NotificationRule(
        days_before=rule.days_before,
        hour=rule.hour
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule


# UPDATE
def update_rule(db: Session, rule_id: int, rule_update: schemas.RuleUpdate) -> NotificationRule:
    db_rule = get_rule(db, rule_id)

    if not db_rule:
        raise RuleNotFoundError(f"Rule with id {rule_id} not found")

    if rule_update.days_before is not None:
        existing_rule = db.query(models.NotificationRule).filter(
            models.NotificationRule.days_before == rule_update.days_before
        ).first()

        if existing_rule and existing_rule.id != rule_id:
            raise DuplicateRuleError("Rule already exists")

        db_rule.days_before = rule_update.days_before

    if rule_update.hour is not None:
        db_rule.hour = rule_update.hour

    db.commit()
    db.refresh(db_rule)

    return db_rule


# DELETE
def delete_rule(db: Session, rule_id: int) -> models.NotificationRule | None:
    db_rule = get_rule(db, rule_id)

    if not db_rule:
        raise RuleNotFoundError(f"Rule with id {rule_id} not found")

    db.delete(db_rule)
    db.commit()

    return db_rule
