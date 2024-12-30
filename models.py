from sqlalchemy import Column, String, Float, ForeignKey
from database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    parent_id = Column(String, ForeignKey('categories.id'), nullable=True)

class Product(Base):
    __tablename__ = "products"

    code = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

class ProductCategory(Base):
    __tablename__ = "products_categories"

    product_code = Column(String, ForeignKey('products.code'), primary_key=True)
    category_id = Column(String, ForeignKey('categories.id'), primary_key=True)
