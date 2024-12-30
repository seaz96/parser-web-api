from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
DbSession = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = DbSession()
    try:
        yield db
    finally:
        db.close()

