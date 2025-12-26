from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import database, models, schemas, crud
from .exceptions import DuplicateRuleError, RuleNotFoundError

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- FRIENDS ---
@app.get("/friends/", response_model=list[schemas.Friend])
def read_friends(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[models.Friend]:
    return crud.get_friends(db, skip=skip, limit=limit)


@app.post("/friends/", response_model=schemas.Friend)
def create_friend(friend: schemas.FriendCreate, db: Session = Depends(get_db)) -> models.Friend:
    return crud.create_friend(db=db, friend=friend)


@app.put("/friends/{friend_id}", response_model=schemas.Friend)
def update_friend(friend_id: int, friend_update: schemas.FriendUpdate, db: Session = Depends(get_db)) -> models.Friend:
    updated_friend = crud.update_friend(db, friend_id, friend_update)

    if updated_friend is None:
        raise HTTPException(status_code=404, detail="Friend not found")

    return updated_friend


@app.delete("/friends/{friend_id}", response_model=schemas.DeleteResponse)
def delete_friend(friend_id: int, db: Session = Depends(get_db)) -> schemas.DeleteResponse:
    db_friend = crud.delete_friend(db, friend_id)

    if db_friend is None:
        raise HTTPException(status_code=404, detail="Friend not found")

    return schemas.DeleteResponse(status="deleted", id=friend_id)


# --- RULES ---
@app.get("/rules/", response_model=list[schemas.Rule])
def read_rules(db: Session = Depends(get_db)):
    return crud.get_rules(db)


@app.post("/rules/", response_model=schemas.Rule)
def create_rule(rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_rule(db=db, rule=rule)
    except DuplicateRuleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/rules/{rule_id}", response_model=schemas.Rule)
def update_rule(rule_id: int, rule_update: schemas.RuleUpdate, db: Session = Depends(get_db)) -> models.NotificationRule:
    try:
        return crud.update_rule(db, rule_id, rule_update)
    except RuleNotFoundError:
        raise HTTPException(status_code=404, detail="Rule not found")
    except DuplicateRuleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/rules/{rule_id}", response_model=schemas.DeleteResponse)
def delete_rule(rule_id: int, db: Session = Depends(get_db)) -> schemas.DeleteResponse:
    try:
        crud.delete_rule(db, rule_id)
        return schemas.DeleteResponse(status="deleted", id=rule_id)
    except RuleNotFoundError:
        raise HTTPException(status_code=404, detail="Rule not found")
