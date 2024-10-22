#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.schema.doc import CreateSysDocParam
from backend.app.admin.schema.doc_data import CreateSysDocDataParam
from backend.app.admin.service.doc_service import sys_doc_service
from backend.common.response.response_schema import response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.utils.doc_utils import post_pdf_recog
import os
from fastapi import File, UploadFile
from pathlib import Path
import pandas as pd
import numpy as np
import asyncio


router = APIRouter()

# 定义上传文件保存的目录
UPLOAD_DIRECTORY = "uploads"

# 创建上传文件的目录，如果不存在则创建
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    获取文件的后缀名。

    :param filename: 文件名字符串
    :return: 文件后缀名（包含 . 号），如 .txt 或 .xlsx
    """
    return os.path.splitext(filename)[1][1:]


def is_excel_file(filename: str) -> bool:
    """
    判断文件是否为 Excel 文件（根据后缀名）。

    :param filename: 文件名字符串
    :return: 如果是 Excel 文件返回 True，否则返回 False
    """
    return Path(filename).suffix.lower() in ['.xls', '.xlsx']


def is_pdf_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.pdf']

def is_picture_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.jpeg', '.jpg', '.png']

def is_media_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.mp4', '.mp3', '.flv']

def is_text_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.txt', '.host', '.config']

def is_code_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.c', '.cpp', '.java', '.py', 'js', '.ts', '.rb', '.go']

def is_email_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.eml']

def get_filename(file_path: str):
    return os.path.basename(file_path)

def get_file_title(file_name: str):
    return os.path.splitext(file_name)[0]


@router.post("/", summary='上传文件', dependencies=[DependsJwtAuth])
async def upload_file(file: UploadFile = File(...)):
    if is_excel_file(file.filename):
        await read_excel(file)
    elif is_picture_file(file.filename):
        await normal_read(file, "picture")
    elif is_media_file(file.filename):
        await normal_read(file, "media")
    elif is_text_file(file.filename):
        await normal_read(file, "text")
    elif is_code_file(file.filename):
        await normal_read(file, "code")
    elif is_email_file(file.filename):
        await normal_read(file, 'email')
    elif is_pdf_file(file.filename):
        await read_pdf(file)
    else:
        await normal_read(file, "text")

    resp = {"filename": file.filename}
    return response_base.success(data=resp)


async def normal_read(file: UploadFile, type: str):
    file_location = await save_file(file)
    name = get_filename(file.filename)
    title = get_file_title(name)
    obj: CreateSysDocParam = CreateSysDocParam(title=title, name=name, type=type,
                                                file=file_location)
    await sys_doc_service.create(obj=obj)


async def read_pdf(file: UploadFile = File(...)):
    file_location = await save_file(file)
    name = get_filename(file.filename)
    title = get_file_title(name)
    obj: CreateSysDocParam = CreateSysDocParam(title=title, name=name, type="pdf",
                                                file=file_location)
    await sys_doc_service.create(obj=obj)
    path = f"~/{file_location}"
    loop = asyncio.get_running_loop()
    pdf_records = await loop.run_in_executor(None, post_pdf_recog, path, "~/uploads/result/", "zhen_light")
    print(pdf_records[0].content)



async def read_excel(file: UploadFile = File(...)):
    # 读取 Excel 文件并解析为 DataFrame
    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        raise e

    # 替换 NaN 为 None（可以避免 PostgreSQL 插入错误）
    df = df.where(pd.notnull(df), None)
    df.replace([np.nan, np.inf, -np.inf], None, inplace=True)

    # 将 DataFrame 转换为 JSON 格式
    data_json = df.to_dict(orient="records")

    # 构建文件保存路径
    file_location = await save_file(file)

    # 将数据存入数据库
    name = get_filename(file.filename)
    title = get_file_title(name)
    doc_param = CreateSysDocParam(title=title, name=name, type='excel', file=file_location)
    doc = await sys_doc_service.create(obj=doc_param)
    for excel_data in data_json:
        param = CreateSysDocDataParam(doc_id=doc.id, excel_data=excel_data)
        await sys_doc_service.create_doc_data(obj=param)
    return response_base.success(data=doc.id)


async def save_file(file: UploadFile = File(...)):
    # 构建文件保存路径
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

    # 提取目录部分并创建目录（如果不存在）
    directory = os.path.dirname(file_location)
    os.makedirs(directory, exist_ok=True)

    # 将上传的文件保存到指定目录
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return file_location