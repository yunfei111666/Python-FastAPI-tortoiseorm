'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-15 17:17:09
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:12:12
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/tools/api.py
'''
from fastapi import APIRouter

from apis import user,login,collect,tag,scene

api_router = APIRouter()
api_router.include_router(login.loginApp,tags=["用户登录"])
api_router.include_router(user.userApp,tags=["用户管理"])
api_router.include_router(collect.collectApp,tags=["场景收藏"])
api_router.include_router(tag.tagApp,tags=["标签管理"])
api_router.include_router(scene.sceneApp,tags=["场景管理"])
