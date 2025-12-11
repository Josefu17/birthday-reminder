from sqlalchemy.orm import Session

from . import models, schemas
from .models import Friend


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
    db_rule = models.NotificationRule(days_before=rule.days_before)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule


# UPDATE
def update_rule(db: Session, rule_id: int, rule_update: schemas.RuleUpdate):
    db_rule = get_rule(db, rule_id)

    if not db_rule:
        return None

    existing_rule_for_days = db.query(models.NotificationRule).filter(
        models.NotificationRule.days_before == rule_update.days_before).first()

    if existing_rule_for_days:
        # TODO handle accordingly (reject update with a message?)
        return None

    # TODO clarify: what to do if db_rule days == rule_update.days -> implicitly update or ignore?

    db_rule.days_before = rule_update.days_before
    db.commit()
    db.refresh(db_rule)

    return db_rule


# TODO continue from here, yb


# DELETE
def delete_rule(db: Session, rule_id: int) -> models.NotificationRule | None:
    db_rule = get_rule(db, rule_id)

    if db_rule:
        db.delete(db_rule)
        db.commit()

    return db_rule
