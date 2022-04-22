'''
Author: yunfei
Date: 2022-03-02 09:25:25
LastEditTime: 2022-04-18 09:36:57
FilePath: /trunkverse_python_FastAPI/trunkverse_service/models/scenario.py
LastAuthor: Do not edit
Description: 
'''
from .public import TimestampMixin,UserMixin
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

class Scenario(TimestampMixin,UserMixin):
    scenario_id = fields.IntField(max_length=20, description="场景id",pk=True)
    scenario_name = fields.CharField(max_length=50, description="场景名称", unique=True)
    mapInfo=fields.JSONField(max_length=2550,default={},description="地图json数据")
    rules=fields.JSONField(max_length=2550,default={},description="json数据")
    imgUrl=fields.TextField(description="服务端图片路径地址")
    description = fields.CharField(max_length=255,description="场景描述")
    tags = fields.CharField(max_length=200,description="场景标签列表")
    is_collect = fields.BooleanField(default=False, description="是否收藏")
    current_version = fields.CharField(max_length=50,default='0.1', description="场景最新的版本号")
    # 修改时保存提交的类型 1：保存新版本 2：覆盖当前版本 3：保存当前场景挈带最新版本
    sc_save_type = fields.CharField(max_length=50, description="保存的类型", default='1')

Scenario_Pydantic = pydantic_model_creator(Scenario, name="Scenario")
ScenarioIn_Pydantic = pydantic_model_creator(Scenario, name="ScenarioIn", exclude_readonly=True)


class ScenarioVersion(TimestampMixin,UserMixin):
    scenario_version = fields.FloatField(default=0.1, description="场景版本号")
    mapInfo=fields.JSONField(max_length=2550,default={},description="地图json数据")
    rules=fields.JSONField(max_length=2550,default={},description="json数据")
    tags = fields.CharField(max_length=255,description="标签列表")
    version_update_comment = fields.CharField(max_length=255,default='',description="场景版本更新说明，选填")
    update_method = fields.CharField(max_length=255, default=0,description="场景创建/修改的来源")
    minimal_frontend_version = fields.CharField(max_length=20, default=0.1,description="最低前端版本要求")
    minimal_backend_version = fields.CharField(max_length=20, default=0.1,description="最低后端版本要求")
    is_latest = fields.BooleanField(default=True,description="用于标记该场景是否为最新版本")
    parent_scenario_id = fields.CharField(max_length=255,description="场景版本号id对应的场景id")
