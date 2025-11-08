# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base  # <-- 导入我们在 database.py 中创建的 Base
import datetime

class User(Base):
    __tablename__ = "users"  # 数据库中的表名

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # 我们绝不存明文密码

    # 定义 "关系"：一个 User 可以有多个 File
    files = relationship("File", back_populates="uploader")

class File(Base):
    __tablename__ = "files"  # 数据库中的表名

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String, unique=True, index=True, nullable=False)
    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # 定义外键，关联到 "users" 表的 "id" 字段
    uploader_id = Column(Integer, ForeignKey("users.id"))

    # 定义 "关系"：一个 File 只属于一个 User
    uploader = relationship("User", back_populates="files")