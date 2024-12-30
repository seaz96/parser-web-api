from pydantic import BaseModel


class CategoryCreate(BaseModel):
    id: str
    name: str
    parent_id: str = None


class ProductCreate(BaseModel):
    code: str
    name: str
    price: float


class CategoryUpdate(BaseModel):
    name: str
    parent_id: str = None

class ProductUpdate(BaseModel):
    name: str
    price: float
