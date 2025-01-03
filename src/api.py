import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, WebSocket
from sqlalchemy.orm import Session
from parser_service import ParserBackgroundService
from database import Base, engine, get_db
from request_models import CategoryCreate, ProductCreate, CategoryUpdate, ProductUpdate
from models import Category, Product, ProductCategory
from response_models import ProductWithCategory
from websockets_manager import WebsocketsManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(parser_service.parse_site(ws_manager))
    yield


parser_service = ParserBackgroundService()
app = FastAPI(lifespan=lifespan)
ws_manager = WebsocketsManager()
Base.metadata.create_all(bind=engine)


@app.post("/categories/")
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    if db.query(Category).filter(Category.id == category.id).first() is None:
        raise HTTPException(status_code=403, detail="Category exists")
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    await ws_manager.broadcast({
        "message": f"Created category {db_category.id}"
    })
    return db_category



@app.get("/categories/")
async def get_categories(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_category = db.query(Category).offset(offset).limit(limit)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await ws_manager.broadcast({
        "message": f"Get categories: offset {offset}, limit {limit}"
    })
    return list(db_category)


@app.get("/categories/{category_id}")
async def read_category(category_id: str, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await ws_manager.broadcast({
        "message": f"Get category by id {db_category.id}"
    })
    return db_category


@app.put("/categories/{category_id}")
async def update_category(category_id: str, category: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    await ws_manager.broadcast({
        "message": f"Updated category {db_category.id}"
    })
    return db_category


@app.delete("/categories/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    await ws_manager.broadcast({
        "message": f"Delete category {db_category.id}"
    })
    return {"ok": True}


@app.post("/products/")
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    await ws_manager.broadcast({
        "message": f"Created product {product.id}"
    })
    return db_product


@app.get("/products/")
async def get_products(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_category = db.query(Product).offset(offset).limit(limit)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await ws_manager.broadcast({
        "message": f"Get products: offset {offset}, limit {limit}"
    })
    return list(db_category)


@app.get("/products/{product_id}")
async def read_product(product_id: str, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product_category = db.query(ProductCategory).filter(ProductCategory.product_id == product_id).first()
    db_category = db.query(Category).filter(Category.id == db_product_category.category_id).first()

    await ws_manager.broadcast({
        "message": f"Get product by id {product_id}"
    })

    return ProductWithCategory(id=db_product.id, name=db_product.name, price=db_product.price,
                               category_id=db_category.id,
                               category_name=db_category.name)


@app.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    await ws_manager.broadcast({
        "message": f"Updated product {product_id}"
    })
    return db_product


@app.delete("/products/{product_id}")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()

    await ws_manager.broadcast({
        "message": f"Deleted product {product_id}"
    })
    return {"ok": True}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive()
            if data.get('type') == 'websocket.disconnect':
                break
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=1235)
