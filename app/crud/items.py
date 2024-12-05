from sqlalchemy.orm import Session
from models.item import Item
from schemas.item import ItemCreate


def read_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()


def read_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Item).offset(skip).limit(limit).all()


def create_item(db: Session, item: ItemCreate):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
