#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import select, Select, text, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model import SysDoc
from backend.app.admin.schema.doc import CreateSysDocParam, UpdateSysDocParam


class CRUDSysDoc(CRUDPlus[SysDoc]):
    async def get(self, db: AsyncSession, pk: int) -> SysDoc | None:
        """
        获取 SysDoc

        :param db:
        :param pk:
        :return:
        """
        where = [self.model.id == pk]
        doc = await db.execute(
            select(self.model)
            .options(selectinload(self.model.doc_data))
            .where(*where)
        )
        return doc.scalars().first()

    async def token_search(self, db: AsyncSession, tokens: str = None) -> list[int]:
        if tokens:
            query = f"""
            SELECT DISTINCT doc_id
            FROM sys_doc_data
            WHERE to_tsvector('simple', tokens::text) @@ plainto_tsquery('{tokens}');
            """
            result = await db.execute(text(query))
            ids = result.scalars().all()
            print("token search ids", ids)
            return ids
        else:
            return None


    async def get_list(self, name: str = None, type: str = None, ids: list[int] = None) -> Select:
        """
        获取 SysDoc 列表
        :return:
        """
        where_list = []
        stmt = select(self.model).order_by(desc(self.model.created_time))
        if name is not None:
            where_list.append(self.model.name.like(f'%{name}%'))
        if type is not None:
            where_list.append(self.model.type == type)
        if ids is not None:
            where_list.append(self.model.id.in_(ids))
        if where_list:
            stmt = stmt.where(and_(*where_list))
        return stmt

    async def get_all(self, db: AsyncSession) -> Sequence[SysDoc]:
        """
        获取所有 SysDoc

        :param db:
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj_in: CreateSysDocParam) -> SysDoc:
        """
        创建 SysDoc

        :param db:
        :param obj_in:
        :return:
        """
        return await self.create_model(db, obj_in)

    async def update(self, db: AsyncSession, pk: int, obj_in: UpdateSysDocParam) -> int:
        """
        更新 SysDoc

        :param db:
        :param pk:
        :param obj_in:
        :return:
        """
        return await self.update_model(db, pk, obj_in)

    async def delete(self, db: AsyncSession, pk: list[int]) -> int:
        """
        删除 SysDoc

        :param db:
        :param pk:
        :return:
        """
        return  await self.delete_model_by_column(db, allow_multiple=True, id__in=pk)


sys_doc_dao: CRUDSysDoc = CRUDSysDoc(SysDoc)
