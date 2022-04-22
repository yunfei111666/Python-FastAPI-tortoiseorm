
'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-09 11:22:04
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:12:06
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/models/users.py
'''
from tortoise import fields
from .public import TimestampMixin
from tortoise.contrib.pydantic import pydantic_model_creator
class Users(TimestampMixin):
    uid = fields.UUIDField(max_length=128,pk=True, description="uid")
    username = fields.CharField(max_length=64, unique=True, description="用户名")
    password = fields.CharField(max_length=64, description="密码")
    hashed_password = fields.CharField(max_length=128,null=True,description="哈希密码")
    is_superuser = fields.BooleanField(default=False, description="是否为超级管理员")
    is_use = fields.BooleanField(default=True,description="账号是否可用")

    def __str__(self):
        return self.username
    
    @classmethod
    async def find_by_user(cls, username):
        return await cls.filter(username=username).first()
    class Meta:
        table = "user"

User_Pydantic = pydantic_model_creator(Users, name="User")
UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)