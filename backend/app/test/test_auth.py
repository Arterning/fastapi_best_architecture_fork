#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import pytest
from faker import Faker
from httpx import AsyncClient

sys.path.append('../../')

from backend.app.core.conf import settings  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.common.redis import redis_client  # noqa: E402


class TestAuth:
    pytestmark = pytest.mark.anyio
    faker = Faker(locale='zh_CN')
    users_api_base_url = f'http://{settings.UVICORN_HOST}:{settings.UVICORN_PORT}/v1/auth/users'

    @property
    async def get_token(self):
        token = await redis_client.get('test_token')
        return token

    async def test_login(self):
        async with AsyncClient(
            app=app, headers={'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        ) as client:
            response = await client.post(
                url=f'{self.users_api_base_url}/login', data={'username': '1', 'password': '1'}
            )
        assert response.status_code == 200
        assert response.json()['token_type'] == 'Bearer'

    async def test_register(self):
        async with AsyncClient(
            app=app, headers={'accept': 'application/json', 'Content-Type': 'application/json'}
        ) as client:
            response = await client.post(
                url=f'{self.users_api_base_url}/register',
                json={
                    'username': f'{self.faker.user_name()}',
                    'password': f'{self.faker.password()}',
                    'email': f'{self.faker.email()}',
                },
            )
        assert response.status_code == 200
        r_json = response.json()
        assert r_json['code'] == 200
        assert r_json['msg'] == 'Success'

    async def test_get_userinfo(self):
        async with AsyncClient(
            app=app, headers={'accept': 'application/json', 'Authorization': f'Bearer {await self.get_token}'}
        ) as client:
            response = await client.get(url=f'{self.users_api_base_url}/1')
        assert response.status_code == 200
        r_json = response.json()
        assert r_json['code'] == 200
        assert r_json['msg'] == 'Success'

    async def test_get_all_users(self):
        async with AsyncClient(
            app=app, headers={'accept': 'application/json', 'Authorization': f'Bearer {await self.get_token}'}
        ) as client:
            response = await client.get(url=f'{self.users_api_base_url}?page=1&size=20')
        assert response.status_code == 200
        r_json = response.json()
        assert isinstance(r_json['data'], list)
        assert isinstance(r_json['links'], dict)
        assert isinstance(r_json['links']['self'], str)