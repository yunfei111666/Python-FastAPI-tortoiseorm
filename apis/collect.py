'''
Author: yunfei
Date: 2022-03-08 15:12:25
LastEditTime: 2022-04-01 09:24:25
FilePath: /python_FastAPI_test/trunkverse_service/apis/collect.py
LastAuthor: Do not edit
Description: 收藏场景
'''
from models.scenario import Scenario
from fastapi import APIRouter,Depends,HTTPException,status
from models.users import Users
from models.collect import Collect,CollectIn_Pydantic
from tools.security import get_current_active_user
from pydantic import BaseModel

collectApp = APIRouter()
class Status(BaseModel):
    code: int
    msg: str

# 场景收藏
@collectApp.post("/collect",summary="场景收藏")
async def set_collect(collect: CollectIn_Pydantic,user: Users = Depends(get_current_active_user)):
    collect.user_uid = user['uid']
    is_have_collect = await Collect.filter(user_uid=collect.user_uid).values()
    if is_have_collect:
        currentIds = is_have_collect[0]['scenario_id']
        if currentIds:
            if collect.is_collect:
                ids = currentIds + ',' + collect.scenario_id
                await Collect.filter(user_uid=collect.user_uid).update(scenario_id=ids)
            else:
                arr = currentIds.split(',')
                filterArr = [elem for elem in arr if elem != collect.scenario_id]
                filterIds = ','.join(filterArr)
                await Collect.filter(user_uid=collect.user_uid).update(scenario_id=filterIds)
        else:
            if collect.is_collect:
                await Collect.filter(user_uid=collect.user_uid).update(scenario_id=collect.scenario_id)
    else:
        await Collect.create(**collect.dict(exclude_unset=True))
    flag:str = '您已' if collect.is_collect else '取消'
    return Status(code=status.HTTP_200_OK,msg= f"{flag}收藏成功！")
        
   
    
   
