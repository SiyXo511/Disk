from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud, schemas, security
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"注册尝试：用户名 '{user.username}'") # <-- 添加日志
    
    # 检查用户是否已存在
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.warning(f"注册失败：用户名 '{user.username}' 已存在") # <-- 添加日志
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 创建用户
    new_user = crud.create_user(db=db, user=user)
    logger.success(f"新用户注册成功：'{new_user.username}' (ID: {new_user.id})") # <-- 添加日志
    return new_user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    logger.debug(f"登录尝试：用户名 '{form_data.username}'") # <-- 添加日志
    
    # 1. 验证用户
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        logger.warning(f"登录失败：用户名或密码错误 (用户名: '{form_data.username}')") # <-- 添加日志
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 创建 Token
    access_token = security.create_access_token(
        data={"sub": user.username}
    )
    
    # 3. 返回 Token
    logger.info(f"用户 '{user.username}' 登录成功") # <-- 添加日志
    return {"access_token": access_token, "token_type": "bearer"}