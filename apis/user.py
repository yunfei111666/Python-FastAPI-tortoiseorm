'''
Description: 获取用户信息
Project: 
Author: yunfei
Date: 2022-03-07 10:06:08
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:10:59
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/apis/user.py
'''

from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.users import Users, User_Pydantic
from tools.security import get_current_active_user, get_password_hash
from tortoise.contrib.fastapi import HTTPNotFoundError
from pydantic import BaseModel
from typing import Optional
from typing import List

userApp = APIRouter()


class Status(BaseModel):
    code: int
    msg: str


class UserIn(BaseModel):
    # 用户名必须是3-20位之间的字母 _ @ .
    username: Optional[str] = Query(..., regex="^[A-Za-z0-9_@.]{3,20}$")
    password: Optional[str] = Query(..., min_length=4, max_length=30)
    hashed_password: Optional[str] = None
    is_superuser: Optional[bool] = False
    is_use: Optional[bool] = True


@userApp.post("/user", response_model=Status, summary="创建用户")
async def create_user(user: UserIn, current_user: Users = Depends(get_current_active_user)):
    is_exists = await Users.filter(username=user.username).exists()
    if is_exists:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_400_BAD_REQUEST,
                'msg': '创建失败，已存在此用户！'
            }
        )
    user.hashed_password = get_password_hash(user.password)
    user.is_superuser = (user.username == 'root') if True else False
    await Users.create(**user.dict(exclude_unset=True))
    return Status(code=status.HTTP_200_OK, msg='创建成功！')


@userApp.get("/me", summary="查询当前登陆者用户信息")
async def read_users_me(current_user: Users = Depends(get_current_active_user)):
    return current_user


@userApp.get("/users", response_model=List[User_Pydantic], summary="用户列表")
async def get_users(user: Users = Depends(get_current_active_user)):
    return await User_Pydantic.from_queryset(Users.all())


@userApp.get("/user/{user_id}", response_model=User_Pydantic, summary="根据uid查用户信息")
async def get_user(user_id: str, current_user: Users = Depends(get_current_active_user)):
    is_exists = await Users.filter(id=user_id).exists()
    if not is_exists:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': f"User {user_id} not found"
            }
        )
    return await User_Pydantic.from_queryset_single(Users.get(uid=user_id))


@userApp.put("/user/{user_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}}, summary="更新用户")
async def update_user(user_id: str, user: UserIn, current_user: Users = Depends(get_current_active_user)):
    if (current_user['username'] != 'root') and (user.is_use == False):
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_403_FORBIDDEN,
                'msg': '暂无权限修改！'
            }
        )
    user.hashed_password = get_password_hash(user.password)
    await Users.filter(uid=user_id).update(**user.dict(exclude_unset=True))
    return Status(code=status.HTTP_200_OK, msg=f"用户{user.username}修改成功！")


@userApp.delete("/user/{user_ids}", response_model=Status, summary="删除用户")
async def delete_user(user_ids: str, current_user: Users = Depends(get_current_active_user)):
    if current_user['username'] != 'root':
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_403_FORBIDDEN,
                'msg': '暂无权限删除！'
            }
        )
    ids = user_ids.split(',')
    print(1111,ids)
    for id in ids:
        deleted_count = await Users.filter(uid=id).delete()
        if not deleted_count:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={
                    'code': status.HTTP_404_NOT_FOUND,
                    'msg': f"User {id} not found"
                }
            )
    return Status(code=status.HTTP_200_OK, msg="删除成功！")    
