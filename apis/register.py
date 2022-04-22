'''
Author: yunfei
Date: 2022-04-22 15:10:31
LastEditTime: 2022-04-22 15:10:37
FilePath: /demo/FastAPI-tortoise-orm/apis/register.py
LastAuthor: Do not edit
Description: 注册
'''
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query,status
from models.users import Users
from tools.security import get_password_hash
from typing import Optional

registerApp = APIRouter(prefix="/api",tags=["注册"])

class Status(BaseModel):
    code: int
    msg: str
class UserIn(BaseModel):
    # 用户名必须是3-20位之间的字母 _ @ .
    username: Optional[str] = Query(..., regex="^[A-Za-z0-9_@.]{3,20}$")
    password: Optional[str] = Query(..., min_length=4, max_length=30)
    is_superuser: Optional[bool] = False
    hashed_password: Optional[str] = None

# 注册
@registerApp.post("/register", summary="注册账号")
async def register(user: UserIn):
    is_exists = await Users.filter(username=user.username).exists()
    if is_exists:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_400_BAD_REQUEST,
                'msg': '注册失败，已存在此用户！'
            }
        )
    else:
        user.hashed_password = get_password_hash(user.password)
        await Users.create(**user.dict(exclude_unset=True))
        return Status(code=status.HTTP_200_OK,msg='注册成功！' )
