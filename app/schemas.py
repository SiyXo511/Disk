from pydantic import BaseModel
import datetime
from typing import Optional

class FileBase(BaseModel):
    original_filename: str
    file_size: int

class FileCreate(FileBase):
    unique_id: str
    stored_path: str
    mime_type: str | None = None
    uploader_id: int

class File(FileBase):
    id: int
    unique_id: str
    created_at: datetime.datetime
    uploader_id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None