'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-04 15:42:37
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:11:47
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/config.py
'''
import secrets
from pydantic import BaseSettings

class Settings(BaseSettings):
    # ip
    HOST = '0.0.0.0'
    # 端口号
    PORT = 8005
    # 是否自动刷新
    IS_RELOAD = True
    # 数据库地址
    #DATABASE_URL = 'mysql://admin:123456@10.11.24.114:3306/fastapi'
    # DATABASE_URL = 'mysql://root:123456@192.168.3.200:3306/fastapi'
    # DATABASE_URL = 'mysql://root:tingting1@127.0.0.1:3306/fastapi'
    DATABASE_URL: str 
    # 项目标题
    APP_NAME: str
    # 秘钥
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # token时效
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100
    # 统一前缀
    BASE_URL:str
    # 加密算法
    ALGORITHM:str = "HS256"

    class Config:
        env_file = ".env"
       

config = Settings()