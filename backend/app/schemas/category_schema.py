from typing import Optional

from pydantic import BaseModel, ConfigDict


# data the api returns for a story category
class CategoryResponse(BaseModel):
    id: int
    slug: str
    label: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int

    # reads values directly from sqlalchemy model instances
    model_config = ConfigDict(from_attributes=True)
