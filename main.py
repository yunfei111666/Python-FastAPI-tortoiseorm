'''
Description: 
Project: 
Author: yunfei
Date: 2022-03-14 15:27:05
LastEditors: Please set LastEditors
LastEditTime: 2022-04-22 15:11:52
Modified By: yunfei
FilePath: /demo/FastAPI-tortoise-orm/main.py
'''
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from models.scenario import Scenario, ScenarioVersion
from datetime import datetime
from tools.api import api_router
from tools.common import deleteFileName
from config import config
from extensions.logger import logger
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

app = FastAPI(title=config.APP_NAME,docs_url=None, redoc_url=None)

# 加载本地swagger相关文件
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_favicon_url="/static/favicon.png",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )
    
@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )
    
# 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=('*'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 引入路由
app.include_router(api_router, prefix=config.BASE_URL)

# 配置图片路径
app.mount('/images', StaticFiles(directory='./images'), name='images') #服务器文件地址 /home/infra/simulation

# 连接数据库
register_tortoise(
    app,
    db_url=config.DATABASE_URL,
    modules={"models": ["models.users","models.tags","models.collect","models.scenario"]},
    generate_schemas=True, #如果数据库为空，则自动生成对应表单,生产环境不要开
    add_exception_handlers=True, #生产环境不要开，会泄露调试信息
)

# 编写通知每天调用一次,30天硬删除数据
async def write_notification():
    while True:
        # 检测大于30天，自动删除
        await asyncio.sleep(86400)  # 一天86400
        scenarioDel_list = await Scenario.all().values()
        if scenarioDel_list:
            for obj in scenarioDel_list:
                t1 = obj['created_at']
                scenarioTime =  datetime.now().timestamp() - t1.timestamp()
                if int(scenarioTime/86400) > 30:
                    await Scenario.filter(scenario_id = obj['scenario_id']).delete()
                    await ScenarioVersion.filter(parent_scenario_id = obj['scenario_id']).delete()
                    # 删除图片
                    scenarioObj = await Scenario.filter(scenario_id = obj['scenario_id']).values()
                    if scenarioObj:
                        for obj in scenarioObj:
                            if obj['imgUrl']:
                                imgName = obj['imgUrl'].split('/')[-1]
                                deleteFileName(imgName)

# 添加一个自动自执行任务
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(write_notification())



# 启动
if __name__ == "__main__":
    import uvicorn
    logger.debug("----服务器重启----")
    uvicorn.run(
        app="main:app", 
        host=config.HOST, 
        port=config.PORT,
        reload=config.IS_RELOAD
    )
