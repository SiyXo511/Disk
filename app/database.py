from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./datebase.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    一个 FastAPI 依赖项，用于获取数据库会话。
    它会在每次请求时创建一个新的会话，并在请求结束后关闭它。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()