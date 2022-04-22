'''
Author: yunfei
Date: 2022-03-02 14:13:42
LastEditTime: 2022-04-22 15:10:42
FilePath: /demo/FastAPI-tortoise-orm/apis/scene.py
LastAuthor: Do not edit
Description: 场景
'''
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Request, HTTPException, status
from tools.common import is_number, getImgSrc, repeatList, timeFormat
from tools.security import get_current_active_user
from models.users import Users
from models.collect import Collect
from models.scenario import Scenario, ScenarioVersion, ScenarioIn_Pydantic
from extensions.logger import logger
sceneApp = APIRouter()


class Status(BaseModel):
    code: int
    msg: str


class sceneBase(BaseModel):
    mapInfo: Optional[dict] = None
    rules: Optional[dict] = None
    tags: Optional[str] = None
    create_user: Optional[str] = None
    update_user: Optional[str] = None
    user_uid: Optional[str] = None
    parent_scenario_id: Optional[str] = None


# 场景管理查询
@sceneApp.get("/scenes", summary="查询当前用户所有场景")
async def scenes(scenario_name: Optional[str] = None, startTime: Optional[str] = None, endTime: Optional[str] = None, tags: Optional[str] = None, user: Users = Depends(get_current_active_user)):
    # 设置所有收藏为false，设置当前用户显示为true
    await Scenario.filter(is_delete=False).update(is_collect=False)
    collectAll = await Collect.filter(user_uid=user["uid"]).values()
    if collectAll:
        currentIds = collectAll[0]["scenario_id"]
        if currentIds:
            currentArr = currentIds.split(",")
            for id in currentArr:
                await Scenario.filter(is_delete=False, scenario_id=id).update(is_collect=True)
    # 场景查询
    if scenario_name or startTime or endTime or tags:
        if startTime and endTime:
            startTime = timeFormat(startTime)
            endTime = timeFormat(endTime)
        if scenario_name and startTime == "" and endTime == "" and tags == "":
            allArr = []
            if is_number(scenario_name):
                idObj = await Scenario.filter(is_delete=False, scenario_id__contains=int(scenario_name)).values()
                if idObj:
                    for s in idObj:
                        allArr.append(s)
            nameObj = await Scenario.filter(is_delete=False, scenario_name__contains=scenario_name).values()
            if nameObj:
                for n in nameObj:
                    allArr.append(n)
            res = repeatList(allArr)
        elif startTime and endTime and scenario_name == "" and tags == "":
            res = await Scenario.filter(is_delete=False, created_at__gte=startTime, created_at__lte=endTime).values()
        elif tags and scenario_name == "" and startTime == "" and endTime == "":
            tagsIds = tags.split(",")
            res = []
            for id in tagsIds:
                resObj = await Scenario.filter(is_delete=False, tags__contains=id).values()
                for obj in resObj:
                    res.append(obj)
        elif scenario_name and startTime and endTime and tags == "":
            allArr = []
            if is_number(scenario_name):
                resObj = await Scenario.filter(is_delete=False, created_at__gte=startTime, created_at__lte=endTime, scenario_id__contains=int(scenario_name)).values()
                for obj in resObj:
                    allArr.append(obj)
            resObj = await Scenario.filter(is_delete=False, created_at__gte=startTime, created_at__lte=endTime, scenario_name__contains=scenario_name).values()
            for obj in resObj:
                allArr.append(obj)
            res = repeatList(allArr)
        elif scenario_name and tags and startTime == "" and endTime == "":
            tagsIds = tags.split(",")
            allArr = []
            for id in tagsIds:
                if is_number(scenario_name):
                    idObj = await Scenario.filter(is_delete=False, scenario_id__contains=int(scenario_name)).values()
                    if idObj:
                        for s in idObj:
                            if set(id).intersection(set(s["tags"])):
                                allArr.append(s)
                nameObj = await Scenario.filter(is_delete=False, scenario_name__contains=scenario_name).values()
                if nameObj:
                    for n in nameObj:
                        if set(id).intersection(set(n["tags"])):
                            allArr.append(n)
            res = repeatList(allArr)
        elif startTime and endTime and tags and scenario_name == "":
            tagsIds = tags.split(",")
            allArr = []
            for id in tagsIds:
                objTime = await Scenario.filter(is_delete=False, created_at__gte=startTime, created_at__lte=endTime).values()
                if objTime:
                    for st in objTime:
                        if set(id).intersection(set(st['tags'])):
                            allArr.append(st)
            res = repeatList(allArr)
        elif startTime and endTime and tags and scenario_name:
            tagsIds = tags.split(",")
            allArr = []
            for id in tagsIds:
                if is_number(scenario_name):
                    objTime = await Scenario.filter(is_delete=False, scenario_id__contains=int(scenario_name), created_at__gte=startTime, created_at__lte=endTime).values()
                    if objTime:
                        for st in objTime:
                            if set(id).intersection(set(st['tags'])):
                                allArr.append(st)
                objTime = await Scenario.filter(is_delete=False, scenario_name__contains=scenario_name, created_at__gte=startTime, created_at__lte=endTime).values()
                if objTime:
                    for st in objTime:
                        if set(id).intersection(set(st['tags'])):
                            allArr.append(st)
            res = repeatList(allArr)

    else:
        res = await Scenario.filter(is_delete=False).values()
    return res

# 查询当前场景最新版本号


@sceneApp.get("/sceneVersionNew", summary="查询当前场景最新版本号")
async def scenesVersion(scenario_id: str):
    res = await ScenarioVersion.filter(parent_scenario_id=scenario_id, is_latest=True, is_delete=False).values()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': f"scenario_id {scenario_id} not found"
            }
        )
    return res

# 查询当前场景所有版本号


@sceneApp.get("/sceneVersionAll", summary="查询当前场景所有版本号")
async def scenesVersionAll(scenario_id: str):
    res = await ScenarioVersion.filter(is_delete=False, parent_scenario_id=scenario_id).values()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={
                'code': status.HTTP_404_NOT_FOUND,
                'msg': f"scenario_id {scenario_id} not found"
            }
        )
    return res


@sceneApp.post("/addScene", summary="新增场景")
async def addScene(scene: ScenarioIn_Pydantic, request: Request, user: Users = Depends(get_current_active_user)):
    scene.create_user = user['username']
    scene.update_user = user['username']
    scene.user_uid = user['uid']
    # 添加对应场景
    scenario = await Scenario.create(**scene.dict(exclude_unset=True))
    scenario_id = scenario.scenario_id
    # 添加对应场景版本信息
    scenario_version = await ScenarioVersion.create(**scene.dict(exclude_unset=True), parent_scenario_id=scenario_id)
    await Scenario.filter(scenario_id=scenario_id).update(imgUrl=getImgSrc(request, scene.imgUrl, str(scenario_id) + '_' + str(scenario_version.scenario_version) + '_' + scene.scenario_name))
    return Status(code=status.HTTP_200_OK, msg='新增成功')


class ScenarioIn(sceneBase):
    scenario_name: str = Field(..., example='场景名称')
    description: str = Field(..., example='场景描述')
    imgUrl: str = Field(..., example='图片baseUrl')
    current_version: Optional[str] = None
    sc_save_type: Optional[str] = None
    is_latest: Optional[bool] = None


class ScenarioVersionEditOut(sceneBase):
    scenario_version: float
    version_update_comment: str
    is_latest: Optional[bool] = None


class EditSceneIn(sceneBase):
    scenario_name: str = Field(..., example='场景名称')
    description: str = Field(..., example='场景描述')
    scenario_id: str = Field(..., example='场景id')
    current_version: Optional[str] = None
    sc_save_type: Optional[str] = None
    imgUrl: Optional[str] = None
    is_latest: Optional[bool] = None


class SceneType():
    """修改类型"""
    CURRENT_VERSION = '1',  '最新版本'
    COVER_VERSION = '2',    '覆盖版本'
    CURRENT_NEW_VERSION = '3', '新增当前场景并携带最新的一个版本'


@sceneApp.put("/editScene", summary="修改场景")
async def editScene(editScene: EditSceneIn, request: Request, user: Users = Depends(get_current_active_user)):
    # 1.检测场景版本是否存在
    is_scenario = await Scenario.filter(scenario_id=editScene.scenario_id).exists()
    if not is_scenario:
        return Status(code=status.HTTP_405_METHOD_NOT_ALLOWED, msg="场景id有误！")
    # 获取最新版本号
    is_latest_gather = await ScenarioVersion.get(parent_scenario_id=editScene.scenario_id, is_latest=True).values()
    new_version = is_latest_gather['scenario_version']
    if editScene.sc_save_type == SceneType.CURRENT_VERSION[0]:  # 1:创建当前场景下最新版本
        logger.debug(f"这是场景修改接口，类型1")
        # 设置对应场景版本号所有的is_latest标记为false
        await ScenarioVersion.filter(parent_scenario_id=editScene.scenario_id, is_latest=True).update(is_latest=False)
        # 修改对应场景
        scene_in = ScenarioIn(
                scenario_name = editScene.scenario_name,
                description = editScene.description,
                imgUrl =  '',
                tags = editScene.tags,
                mapInfo = editScene.mapInfo,
                rules = editScene.rules,
                create_user = user['username'],
                update_user = user['username'],
                user_uid = str(user['uid'])
            )

        await Scenario.filter(scenario_id=editScene.scenario_id).update(**scene_in.dict(exclude_unset=True))
        # 添加提交最新版本号，设置最新版本标记为true
        sv_in = ScenarioVersionEditOut(
            scenario_version=(float(new_version) * 10 + 0.1*10)/10,
            mapInfo=editScene.mapInfo,
            rules=editScene.rules,
            tags=editScene.tags,
            version_update_comment='comment',
            user_uid=str(user['uid']),
            create_user=user['username'],
            update_user=user['username'],
            is_latest=True,
            parent_scenario_id=editScene.scenario_id
        )
        scenario_v = await ScenarioVersion.create(**sv_in.dict(exclude_unset=True))
        await Scenario.filter(scenario_id=editScene.scenario_id).update(imgUrl=getImgSrc(request, editScene.imgUrl, str(editScene.scenario_id) + '_' + str(scenario_v.scenario_version) + '_' + editScene.scenario_name))
        return Status(code=status.HTTP_200_OK, msg="修改成功！")

    elif editScene.sc_save_type == SceneType.COVER_VERSION[0]:  # 2:代表覆盖当前版本
        logger.debug(f"这是场景修改接口，类型2")
        # 修改对应场景
        scene_in = ScenarioIn(
            scenario_name=editScene.scenario_name,
            description=editScene.description,
            imgUrl="",
            tags=editScene.tags,
            sc_save_type=editScene.sc_save_type,
            mapInfo=editScene.mapInfo,
            rules=editScene.rules,
            current_version=new_version,
            update_user=user['username'],
            user_uid=str(user['uid'])
        )
        await Scenario.filter(scenario_id=editScene.scenario_id).update(**scene_in.dict(exclude_unset=True))
        await ScenarioVersion.filter(parent_scenario_id=editScene.scenario_id, is_latest=True).update(
            scenario_version=float(new_version),
            mapInfo=editScene.mapInfo,
            rules=editScene.rules,
            tags=editScene.tags,
            version_update_comment='comment',
            update_user=user['username']
        )
        await Scenario.filter(scenario_id=editScene.scenario_id).update(imgUrl=getImgSrc(request, editScene.imgUrl, str(editScene.scenario_id) + '_' + str(new_version) + '_' + editScene.scenario_name))
        return Status(code=status.HTTP_200_OK, msg="修改成功！")
    else:  # 3：代表保存新增当前场景并携带最新的一个版本
        logger.debug(f"这是场景修改接口，类型3")
        # 新建对应场景
        sceneIn = ScenarioIn(
            scenario_name=editScene.scenario_name,
            description=editScene.description,
            imgUrl="",
            tags=editScene.tags,
            sc_save_type=editScene.sc_save_type,
            mapInfo=editScene.mapInfo,
            rules=editScene.rules,
            current_version=new_version,
            create_user=user['username'],
            update_user=user['username'],
            user_uid=str(user['uid'])
        )
        scenario = await Scenario.create(**sceneIn.dict(exclude_unset=True))
        scenario_id_me = scenario.scenario_id
        # 创建携带最新的一个版本
        sv_in = ScenarioVersionEditOut(
            scenario_version=float(new_version),
            mapInfo=editScene.mapInfo,
            rules=editScene.rules,
            tags=editScene.tags,
            version_update_comment='comment',
            user_uid=str(user['uid']),
            create_user=user['username'],
            update_user=user['username'],
            is_latest=True,
            parent_scenario_id=scenario_id_me
        )
        await ScenarioVersion.create(**sv_in.dict(exclude_unset=True))
        getImgUrl = getImgSrc(request, editScene.imgUrl, str(editScene.scenario_id) + '_' + str(new_version) + '_' + editScene.scenario_name)
        await Scenario.filter(scenario_id=scenario_id_me).update(imgUrl=getImgUrl)
        return Status(code=status.HTTP_200_OK, msg="修改成功！")


class ScenarioId(BaseModel):
    scenario_id: str   # "1,2,3,4"


@sceneApp.delete("/deleteScene", summary="删除场景")
async def deleteScene(delScene: ScenarioId):
    logger.debug(f"这是场景删除接口")
    sceneIds = delScene.scenario_id.split(",")
    # 1.数据库：根据id，软删对应场景及场景下的所有版本，设置30内可以恢复，以外永久删除
    # 2.删除2种方式，单删是删除当前对应场景的当前版本，批量删除是删除场景及场景对应的所有版本
    for scId in sceneIds:
        # 添加删除的场景信息
        await Scenario.filter(scenario_id=scId).update(is_delete=True)
        await ScenarioVersion.filter(parent_scenario_id=scId).update(is_delete=True)
    return Status(code=status.HTTP_200_OK, msg='删除成功')