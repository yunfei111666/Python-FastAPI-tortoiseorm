'''
Author: yunfei
Date: 2022-03-04 15:36:05
LastEditTime: 2022-03-31 17:09:04
FilePath: /python_FastAPI_test/trunkverse_service/models/collect.py
LastAuthor: Do not edit
Description: 收藏
'''

from tortoise import fields
from .public import TimestampMixin
from tortoise.contrib.pydantic import pydantic_model_creator

class Collect(TimestampMixin):
    id = fields.IntField(max_length=64,pk=True,description="收藏id",)
    scenario_id = fields.CharField(max_length=255,unique=True,description="场景id字符窜列表")
    user_uid = fields.CharField(max_length=128,null=True,description="用户uid")
    is_collect = fields.BooleanField(default=False, description="是否收藏")
    
Collect_Pydantic = pydantic_model_creator(Collect, name="Collect")
CollectIn_Pydantic = pydantic_model_creator(Collect, name="CollectIn", exclude_readonly=True)