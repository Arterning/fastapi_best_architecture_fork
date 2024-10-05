#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.schema.doc import CreateSysDocParam
from backend.app.admin.service.doc_service import sys_doc_service
from backend.common.response.response_schema import response_base
from backend.common.security.jwt import DependsJwtAuth
import os
from fastapi import File, UploadFile
from pathlib import Path

router = APIRouter()

# 定义上传文件保存的目录
UPLOAD_DIRECTORY = "uploads"

# 创建上传文件的目录，如果不存在则创建
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)


@router.post("/", summary='上传文件', dependencies=[DependsJwtAuth])
async def upload_file(file: UploadFile = File(...)):
    # 构建文件保存路径
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    file_type = file.content_type
    obj: CreateSysDocParam = CreateSysDocParam(title=file.filename, name=file.filename, type=file_type, file=file_location)
    await sys_doc_service.create(obj=obj)

    # 将上传的文件保存到指定目录
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    resp = {"filename": file.filename, "location": file_location}
    return response_base.success(data=resp)
