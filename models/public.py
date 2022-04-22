'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-14 15:27:05
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:11:09
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/models/public.py
'''
from tortoise.models import Model
from tortoise import fields
from typing import Optional
from pydantic import BaseModel
class TimestampMixin(Model):
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    class Meta:
        abstract = True

class UserMixin(Model):
    create_user = fields.CharField(max_length=50,null=True,description="创建者")
    update_user = fields.CharField(max_length=50,null=True,description="更新者")
    user_uid = fields.CharField(max_length=100,null=True,description="创建者的uid")
    is_delete = fields.BooleanField(default=False, description="标记是否软删默认为false")
    class Meta:
        abstract = True

class Enum(BaseModel):
    key: str
    value: str