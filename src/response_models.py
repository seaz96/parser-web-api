from pydantic import BaseModel


class ProductWithCategory(BaseModel):
    id: str
    name: str
    price: float
    category_id: str
    category_name: str
