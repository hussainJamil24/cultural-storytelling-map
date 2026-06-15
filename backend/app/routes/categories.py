from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.category_model import Category
from app.schemas.category_schema import CategoryResponse

# registers category api routes
router = APIRouter()


# returns all story categories for filters and the upload form
@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    try:
        return db.query(Category).order_by(Category.sort_order, Category.label).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch categories")
