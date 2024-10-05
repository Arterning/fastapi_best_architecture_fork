#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.admin.schema.doc import CreateSysDocParam, GetSysDocListDetails, UpdateSysDocParam
from backend.app.admin.service.doc_service import sys_doc_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db_pg import CurrentSession

router = APIRouter()


@router.get('/{pk}', summary='获取文件详情', dependencies=[DependsJwtAuth])
async def get_sys_doc(pk: Annotated[int, Path(...)]) -> ResponseModel:
    sys_doc = await sys_doc_service.get(pk=pk)
    return response_base.success(data=sys_doc)


@router.get(
    '',
    summary='（模糊条件）分页获取所有文件',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_sys_doc(db: CurrentSession, name: Annotated[str | None, Query()] = None) -> ResponseModel:
    sys_doc_select = await sys_doc_service.get_select(name=name)
    page_data = await paging_data(db, sys_doc_select, GetSysDocListDetails)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建文件',
    dependencies=[
        Depends(RequestPermission('sys:doc:add')),
        DependsRBAC,
    ],
)
async def create_sys_doc(obj: CreateSysDocParam) -> ResponseModel:
    await sys_doc_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新文件',
    dependencies=[
        Depends(RequestPermission('sys:doc:edit')),
        DependsRBAC,
    ],
)
async def update_sys_doc(pk: Annotated[int, Path(...)], obj: UpdateSysDocParam) -> ResponseModel:
    count = await sys_doc_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='（批量）删除文件',
    dependencies=[
        Depends(RequestPermission('sys:doc:del')),
        DependsRBAC,
    ],
)
async def delete_sys_doc(pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await sys_doc_service.delete(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
