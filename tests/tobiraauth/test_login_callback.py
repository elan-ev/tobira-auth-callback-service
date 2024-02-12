#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from pytest_httpx import HTTPXMock
from sanic import Sanic

from tobiraauth.login_callback import login_callback_bp


@pytest.fixture
def app():
    sanic_app = Sanic('test')
    sanic_app.blueprint(login_callback_bp)
    sanic_app.config.USER_LOGIN_WS_URL = 'http://localhost:4567/user/login/{username}'
    return sanic_app


@pytest.mark.asyncio
async def test_login_callback_no_body(app):
    request, response = await app.asgi_client.post('/login')
    assert response.status == 400
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'no-user'


@pytest.mark.asyncio
async def test_login_callback_valid_data(app, httpx_mock: HTTPXMock):
    login_ws_response = {
        'username': 'jane',
        'given_name': 'Jane',
        'sur_name': 'Doe',
        'email': 'jane@edu.org',
    }
    httpx_mock.add_response(method='POST', url='http://localhost:4567/user/login/jane', json=login_ws_response)
    data = {
        'userid': 'jane',
        'password': 'secret'
    }
    request, response = await app.asgi_client.post('/login', json=data)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == 'jane'
    assert userdata.get('displayName') == 'Jane Doe'
    assert userdata.get('email') == 'jane@edu.org'
    assert userdata.get('userRole') == 'ROLE_USER_JANE'
    roles = userdata.get('roles')
    assert 'ROLE_ANONYMOUS' in roles
    assert 'ROLE_USER' in roles
    assert 'ROLE_USER_JANE' in roles
    assert 'ROLE_AAI_USER_jane' in roles


@pytest.mark.asyncio
async def test_login_callback_invalid_username(app, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method='POST',
                            url='http://localhost:4567/user/login/jane_invalid_username', status_code=404)
    data = {
        'userid': 'jane_invalid_username',
        'password': 'secret'
    }
    request, response = await app.asgi_client.post('/login', json=data)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'no-user'
    assert 'username' not in userdata


@pytest.mark.asyncio
async def test_login_callback_invalid_password(app, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method='POST',
                            url='http://localhost:4567/user/login/jane_invalid_password', status_code=401)
    data = {
        'userid': 'jane_invalid_password',
        'password': 'secret'
    }
    request, response = await app.asgi_client.post('/login', json=data)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'no-user'
    assert 'username' not in userdata
