from fastapi import (
    APIRouter, Depends, HTTPException, status, 
    UploadFile, File as FastAPIFile
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import shutil  
from pathlib import Path

from app import crud, schemas, models
from app.database import get_db
from app.security import get_current_user 

router = APIRouter()

SAFE_UPLOAD_DIR = Path("./safe_uploads/")

@router.post(
    "/upload",
    response_model=schemas.File
)
def upload_file(
    file: UploadFile = FastAPIFile(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    stored_filename = f"{file_id}{file_extension}"
    stored_path = SAFE_UPLOAD_DIR / stored_filename

    try:
        SAFE_UPLOAD_DIR.mkdir(exist_ok=True)

        with stored_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}"
        )

    finally:
        file.file.close()

    file_data = schemas.FileCreate(
        unique_id=file_id,
        original_filename=file.filename,
        stored_path=str(stored_path), 
        mime_type=file.content_type,
        file_size=file.size,
        uploader_id=current_user.id 
    )

    db_file = crud.create_file(db, file_data)
    return db_file

@router.get(
    "/download/{file_unique_id}"
)
async def download_file(
    file_unique_id: str,
    db: Session = Depends(get_db)
):
    db_file = crud.get_file_from_unique_id(db, file_unique_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = Path(db_file.stored_path)
    if not file_path.is_file():
        raise HTTPException(status_code=500, detail="File not found on disk")

    download_name = db_file.original_filename
    media_type = db_file.mime_type

    return FileResponse(
        path = file_path,
        filename = download_name,
        media_type = media_type,
        content_disposition_type = "inline"
    )

@router.get(
    "/view/{file_unique_id}",
    response_model=schemas.File
)
def view_file(
    file_unique_id: str,
    db: Session = Depends(get_db)
):
    db_file = crud.get_file_from_unique_id(db, file_unique_id)

    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file
