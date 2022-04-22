'''
Author: yunfei
Date: 2022-04-22 15:10:02
LastEditTime: 2022-04-22 15:10:25
FilePath: /demo/FastAPI-tortoise-orm/apis/login.py
LastAuthor: Do not edit
Description: 登录
'''
from fastapi import APIRouter,HTTPException,Request,status
from datetime import timedelta
from models.users import Users
from config import config
from tools.security import create_access_token,authenticate_user,get_password_hash
from pydantic import BaseModel

loginApp = APIRouter()
class Status(BaseModel):
    code: int
    msg: str
class AuthModel(BaseModel):
    username: str
    password: str
class RootUser(BaseModel):
    username: str
    password: str
    hashed_password: str
    is_superuser: bool
    is_use: bool

@loginApp.post("/login",summary="登陆并获取token")
async def login(auth: AuthModel):
    is_root = await Users.filter(username='root').exists()
    if not is_root:
        root_user = RootUser(
            username = 'root',
            password = '12345',
            hashed_password = get_password_hash('12345'),
            is_superuser = True,
            is_use = True
        )
        await Users.create(**root_user.dict(exclude_unset=True))
    username = auth.username
    password = auth.password
    code = await authenticate_user(username,password)
    if code == 1 or code == 2 or code == 3 :
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': '该账号不可用！' if code == 1 else '该账号不存在！' if code == 2 else '密码有误！'
            }
        )
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {
        'code': status.HTTP_200_OK,
        'msg': '登陆成功！',
        "token_type": "bearer",
        "access_token": access_token
    }

@loginApp.post("/logout",summary="退出登陆")
def logout(request: Request):
    # token = request.cookies.get('Authorization')
    # response = RedirectResponse(url="/login", status_code=status['UNAUTHORIZED'])
    # response.delete_cookie(key="Authorization")
    return Status(
        code=status.HTTP_200_OK,
        msg='登出成功！'
    )