from  sqlalchemy.orm import session
from app import schemas, models
from app.security import get_password_hash

def get_file_from_unique_id(db: session, unique_id: str):
    return db.query(models.File).filter(models.File.unique_id == unique_id).first()

def create_file(db: session, file: schemas.FileCreate):
    db_file = models.File(
        unique_id=file.unique_id,
        original_filename=file.original_filename,
        stored_path=file.stored_path,
        mime_type=file.mime_type,
        file_size=file.file_size,
        uploader_id=file.uploader_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_user_by_username(db: session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username, 
        password_hash=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_files_by_user_id(db: session, user_id: int):
    return db.query(models.File).filter(models.File.uploader_id == user_id).order_by(models.File.created_at.desc()).all()