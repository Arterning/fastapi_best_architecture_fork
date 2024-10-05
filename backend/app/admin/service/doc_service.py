#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import Select

from backend.app.admin.crud.crud_doc import sys_doc_dao
from backend.app.admin.model import SysDoc
from backend.app.admin.schema.doc import CreateSysDocParam, UpdateSysDocParam
from backend.common.exception import errors
from backend.database.db_pg import async_db_session


class SysDocService:
    @staticmethod
    async def get(*, pk: int) -> SysDoc:
        async with async_db_session() as db:
            sys_doc = await sys_doc_dao.get(db, pk)
            if not sys_doc:
                raise errors.NotFoundError(msg='文件不存在')
            return sys_doc

    @staticmethod
    async def get_select(*, name: str = None) -> Select:
        return await sys_doc_dao.get_list(name=name)

    @staticmethod
    async def get_all() -> Sequence[SysDoc]:
        async with async_db_session() as db:
            sys_docs = await sys_doc_dao.get_all(db)
            return sys_docs

    @staticmethod
    async def create(*, obj: CreateSysDocParam) -> None:
        async with async_db_session.begin() as db:
            # sys_doc = await sys_doc_dao.get_by_name(db, obj.name)
            # if sys_doc:
            #     raise errors.ForbiddenError(msg='文件已存在')
            await sys_doc_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateSysDocParam) -> int:
        async with async_db_session.begin() as db:
            count = await sys_doc_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await sys_doc_dao.delete(db, pk)
            return count


sys_doc_service = SysDocService()
