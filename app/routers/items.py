from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from crud.items import create_item, read_item, read_items
from auth_user import get_current_user
from schemas.item import ItemCreate, Item

from database import get_db


items_router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@items_router.post("/", response_model=Item)
def post_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    return create_item(db=db, item=item)


@items_router.get("/{item_id}", response_model=Item)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    db_item = read_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@items_router.get("/", response_model=list[Item])
def get_items(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    items = read_items(db, skip=skip, limit=limit)
    return items
