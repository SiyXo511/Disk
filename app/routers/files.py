from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud, database

router = APIRouter()

@router.get(
    "/view/{file_unique_id}",
    response_model=schemas.File,
)
def view_file(
    file_unique_id: str,
    db: Session = Depends(database.get_db)
):
    db_file = crud.get_file_from_unique_id(db, file_unique_id)

    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file
