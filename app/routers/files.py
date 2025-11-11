from fastapi import (
    APIRouter, Depends, HTTPException, status, 
    UploadFile, File as FastAPIFile
)
from fastapi.responses import FileResponse, JSONResponse
from loguru import logger
from sqlalchemy.orm import Session
import uuid
import shutil  
from pathlib import Path

from app import crud, schemas, models
from app.database import get_db
from app.security import get_current_user 


router = APIRouter()

SAFE_UPLOAD_DIR = Path("./safe_uploads/")


# --- 1. 文件上传 API ---
@router.post("/upload", response_model=schemas.File)
def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    logger.info(f"用户 '{current_user.username}' (ID: {current_user.id}) 开始上传文件。")
    logger.debug(f"文件名: '{file.filename}', 类型: {file.content_type}, 大小: {file.size} bytes")

    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    
    stored_filename = f"{file_id}{file_extension}"
    stored_path = SAFE_UPLOAD_DIR / stored_filename
    
    try:
        SAFE_UPLOAD_DIR.mkdir(exist_ok=True)
        
        with stored_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        # 这是一个非常重要的日志！
        logger.error(f"保存文件到磁盘失败 (用户: {current_user.username}): {e}")
        # Loguru 会自动捕获并格式化异常堆栈
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

    db_file = crud.create_file(db=db, file=file_data)
    
    logger.success(f"文件保存成功。用户: '{current_user.username}', "
                   f"原始文件名: '{db_file.original_filename}', "
                   f"UUID: {db_file.unique_id}")
    
    return db_file

@router.get("/", response_model=list[schemas.File])
def list_my_files(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    logger.info(f"用户 '{current_user.username}' (ID: {current_user.id}) 请求查看自己的文件列表。")
    files = crud.get_files_by_user_id(db=db, user_id=current_user.id)
    return files

@router.delete("/{file_unique_id}")
def delete_file(
    file_unique_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    logger.info(f"用户 '{current_user.username}' (ID: {current_user.id}) 请求删除文件 (UUID: {file_unique_id})。")

    db_file = crud.get_file_from_unique_id(db, unique_id=file_unique_id)
    if db_file is None:
        logger.warning(f"删除失败：文件在数据库中未找到 (UUID: {file_unique_id})")
        raise HTTPException(status_code=404, detail="File not found")

    if db_file.uploader_id != current_user.id:
        logger.error(f"删除失败：用户 '{current_user.username}' (ID: {current_user.id}) 尝试删除不属于他的文件 (UUID: {file_unique_id})")
        raise HTTPException(status_code=403, detail="Not authorized to delete this file")

    try:
        file_path = Path(db_file.stored_path)
        file_path.unlink()
        logger.info(f"已从磁盘删除: {file_path}")
    except FileNotFoundError:
        logger.warning(f"文件在磁盘上已丢失 (路径: {db_file.stored_path})，但仍会从数据库中删除")
    except Exception as e:
        logger.error(f"从磁盘删除文件时出错: {e}")
        raise HTTPException(status_code=500, detail=f"Could not delete file from disk: {e}")

    db.delete(db_file)
    db.commit()

    logger.success(f"文件 (UUID: {file_unique_id}) 已被用户 '{current_user.username}' 成功删除")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "File deleted successfully"}
    )
    
@router.get("/download/{file_unique_id}")
async def download_file(
    file_unique_id: str, 
    db: Session = Depends(get_db)
):
    logger.info(f"公开文件访问尝试 (UUID: {file_unique_id})")
    
    db_file = crud.get_file_from_unique_id(db, unique_id=file_unique_id)
    
    if db_file is None:
        logger.warning(f"访问失败：文件在数据库中未找到 (UUID: {file_unique_id})")
        raise HTTPException(status_code=404, detail="File not found in database")
        
    file_path = Path(db_file.stored_path)
    if not file_path.is_file():
        # 这是一个严重的服务器错误！数据库和磁盘不同步。
        logger.error(f"严重错误：文件记录存在但文件在磁盘上丢失！"
                     f"(UUID: {file_unique_id}, 路径: {file_path})")
        raise HTTPException(status_code=500, detail="File not found on disk")

    logger.debug(f"正在提供文件 (UUID: {file_unique_id})，"
                 f"路径: {file_path}")
    
    return FileResponse(
        path=file_path,
        filename=db_file.original_filename,
        media_type=db_file.mime_type,
        content_disposition_type="inline"
    )

# --- 2. (JSON元数据) 文件查看 API ---
@router.get("/view/{file_unique_id}", response_model=schemas.File)
def view_file(
    file_unique_id: str, 
    db: Session = Depends(get_db)
):
    logger.debug(f"元数据(JSON)查看尝试 (UUID: {file_unique_id})")
    db_file = crud.get_file_by_unique_id(db, unique_id=file_unique_id)
    
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    return db_file