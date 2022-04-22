'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-11 10:56:54
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:10:56
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/apis/tag.py
'''
from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel
from models.users import Users
from models.tags import Tags,Tag_Pydantic,TagIn_Pydantic
from tools.security import get_current_active_user
from typing import Optional

tagApp = APIRouter()

class RootTagOut(BaseModel):
    id: int
    name: str
    pid: int
    description: Optional[str] = None

class TagIn(BaseModel):
    name: str
    pid: int
    description: Optional[str] = None

class Status(BaseModel):
    code: int
    msg: str
    
@tagApp.post("/tag",response_model=Status,summary="新增标签")
async def create_tag(tag:TagIn_Pydantic,user: Users = Depends(get_current_active_user)):
    await Tags.create(**tag.dict(exclude_unset=True))
    return Status(code = status.HTTP_200_OK,msg=f"标签{tag.name}新增成功!") 

@tagApp.delete("/tag/{tag_id}",response_model=Status,summary="删除标签")
async def delete_tag(tag_id: int,user: Users = Depends(get_current_active_user)):
    deleted_count = await Tags.filter(id=tag_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code = status.HTTP_200_OK, 
            detail = {
                'code': status.HTTP_404_NOT_FOUND,
                'msg': f"Tag {tag_id} not found"
            }
        )
    return Status(code = status.HTTP_200_OK,msg=f"标签{tag_id}删除成功！")

@tagApp.put("/tag/{tag_id}",response_model=Status,summary="修改标签")
async def update_tag(tag_id: int,tag: TagIn,user: Users = Depends(get_current_active_user)):
    put_count = await Tags.filter(id=tag_id).update(**tag.dict(exclude_unset=True))
    if not put_count:
        raise HTTPException(
            status_code = status.HTTP_200_OK, 
            detail = {
                'code': status.HTTP_404_NOT_FOUND,
                'msg': f"Tag {tag_id} not found"
            }
        )
    return Status(code = status.HTTP_200_OK,msg=f"标签{tag_id}更新成功！") 
   

@tagApp.get("/tags",summary="获取标签列表")
async def get_tags(type: str,user: Users = Depends(get_current_active_user)):
    is_root = await Tags.filter(pid=0).exists()
    if not is_root:
        tag_in = RootTagOut(
            id = 1,
            pid = 0,
            name = "Tag Tree",
            description = "这是根节点"
        )
        await Tags.create(**tag_in.dict(exclude_unset=True))
    tags = await Tags.all().values()
    if type == 'list':
        return tags
    else:
        tree = [item for item in tags if item['pid'] is 0]
        for item in tags:
            item['children'] = [n for n in tags if item['id'] == n['pid']]
        return tree
   
@tagApp.get("/tag/{tag_id}",summary="标签详情")
async def get_tag(tag_id: int,user: Users = Depends(get_current_active_user)):
    is_exists = await Tags.filter(id=tag_id).exists()
    if not is_exists:
        raise HTTPException(
            status_code = status.HTTP_200_OK, 
            detail = {
                'code': status.HTTP_404_NOT_FOUND,
                'msg': f"Tag {tag_id} not found"
            }
        )
    return await Tag_Pydantic.from_queryset_single(Tags.get(id=tag_id))
       
     