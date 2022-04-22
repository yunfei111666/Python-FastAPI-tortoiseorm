'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-10 18:23:07
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:11:23
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/models/tags.py
'''
from tortoise import fields
from .public import TimestampMixin
from tortoise.contrib.pydantic import pydantic_model_creator

class Tags(TimestampMixin):
    id = fields.IntField(max_length=64,pk=True,description="主键")
    pid = fields.IntField(max_length=64,null=True, description="父id")
    name = fields.CharField(max_length=64,description="标签名")
    description = fields.CharField(max_length=128,null=True,description="描述信息")

Tag_Pydantic = pydantic_model_creator(Tags, name="Tag")
TagIn_Pydantic = pydantic_model_creator(Tags, name="TagIn", exclude_readonly=True)