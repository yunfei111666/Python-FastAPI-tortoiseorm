<!--
 * @Author: yunfei
 * @Date: 2022-04-22 15:22:37
 * @LastEditTime: 2022-04-22 18:25:22
 * @FilePath: /demo/Python-FastAPI-tortoiseorm/README.md
 * @LastAuthor: Do not edit
 * @Description: 
-->

# introduce
```
使用 fastapi + tortoise-orm构建，Docker+GitLab-CI持续集成，自动化部署
FastAPI: 是一个现代、快速（高性能）的 Web 框架，用于基于标准 Python 类型提示使用 Python 3.6+ 构建 API。
tortoise-orm 是一个强大的 异步 ORM 框架，用于构建高性能的数据库模型。


```

# install

```
pip3 install -r requirements.txt 

```

# run

```
python3 main.py
# or
uvicorn main:app --reload --host 0.0.0.0
```

# docs

根据代码自动生成交互式文档

```
http://127.0.0.1:8000/docs
```

# Docker

定制镜像
```
docker build -t ImageName .
```
运行
```
docker run -itd -p port:port ImageName
```
