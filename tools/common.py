'''
Author: yunfei
Date: 2022-03-19 18:50:18
LastEditTime: 2022-04-11 13:34:30
FilePath: /trunkverse_python_FastAPI/trunkverse_service/tools/common.py
LastAuthor: Do not edit
Description: 
'''

import time
import os
import unicodedata
import base64
from PIL import Image
from pathlib import Path
from extensions.logger import logger

# 检测字符串是否为数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

# 删除压缩后文件下所有图
def deleteAllImg(file_name):
    for root, dirs, files in os.walk(file_name):
        for name in files:
            if name.endswith(".png"): # 填写规则
                os.remove(os.path.join(root, name))

# 删除指定图片
def deleteFileName(file_name):
    pathRoot = Path(__file__).resolve().parent.parent
    name = pathRoot / 'images' / file_name
    if os.path.exists(name):
        os.remove(name)
        logger.debug(f"成功删除文件:{name}")
    else:
        logger.debug(f"未找到此文件:{name}")

def get_host(req) -> str:
    return getattr(req, "headers", {}).get("host") or "http://192.168.3.200:8098/"


def resize_image(infile, outfile='', x_s=800):
    """修改图片尺寸
    :param infile: 图片源文件
    :param outfile: 重设尺寸文件保存地址
    :param x_s: 设置的宽度
    :return:
    """
    im = Image.open(infile)
    x, y = im.size
    y_s = int(y * x_s / x)
    out = im.resize((x_s, y_s), Image.ANTIALIAS)
    out.save(outfile)
    im.close()



def getImgSrc(request,imgUrl,scenario_name):
    logger.debug(f"图片地址目录为:{Path(__file__).resolve().parent.parent}")
    # t = str(round(time.time() * 1000)) #时间戳
     # 文件图片上传业务
    base_dir = Path(__file__).resolve().parent.parent
    #/home/infra/images
    media_uploads = base_dir / 'images'
    media_uploads.mkdir(exist_ok=True)
    media_outloads = base_dir / 'images' / 'originImages'
    media_outloads.mkdir(exist_ok=True)
    base64Str = imgUrl.split(",")[1]
    imgdata = base64.b64decode(base64Str, altchars=None, validate=False)
    file = open(str(media_uploads) + f'/{scenario_name}.png','wb')
    file.write(imgdata)
    file.close()
    host = get_host(request)
    # 图片压缩
    
    resize_image(str(media_uploads) + f'/{scenario_name}.png', str(media_outloads) + f'/{scenario_name}.png')
    # 删除源图片文件下的所有文件
    deleteAllImg(media_outloads)
    # 返回图片地址
    return f"{host}/images/{scenario_name}.png"

# 数组去重
def repeatList(data):
    new_data = []
    for i in range(len(data)):
        if data[i] not in new_data:
            new_data.append(data[i])
    return new_data

def timeFormat(date):
     startMs = time.localtime(int(date)/1000)
     timeFm = time.strftime("%Y-%m-%d %H:%M:%S", startMs)
     return timeFm