'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-04 15:47:11
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:12:17
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/tools/security.py
'''
from datetime import datetime, timedelta
from typing import List, Optional
from jose import jwt, JWTError
from fastapi.security import (SecurityScopes, OAuth2PasswordBearer)
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from fastapi import Depends, HTTPException, Security, status
from models.users import Users
from config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class UserIn(BaseModel):
    username: str
    is_superuser: Optional[bool] = False


class TokenData(BaseModel):
    uid: Optional[str] = None
    scopes: List[str] = []

# 生成token
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

# 校验密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 密码加密
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user(username: str):
    return await Users.filter(username=username).first()

# 校验用户名及密码是否正确
async def authenticate_user(username: str, password: str):
    user = await Users.filter(username=username).first()
    if not user:
        return 2
    if not user.is_use:
        return 1
    if not verify_password(password, user.hashed_password):
        return 3
    return user


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_200_OK,
        headers={"WWW-Authenticate": 'Bearer'},
        detail={
            'code': status.HTTP_401_UNAUTHORIZED,
            'msg': '无法验证凭据'
        }
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY,
                             algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = await Users.filter(username=username).values()
    if not user:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={
                    'code': status.HTTP_401_UNAUTHORIZED,
                    'msg': '权限不足'
                },
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user[0]

# 获取当前登陆用户


async def get_current_active_user(
    current_user: UserIn = Security(get_current_user)
):
    # 超级用户
    # if current_user['is_superuser']:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
