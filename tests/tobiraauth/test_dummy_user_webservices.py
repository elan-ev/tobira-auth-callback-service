#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from sanic import Sanic

from tobiraauth.dummy_user_webservices import dummy_user_ws_blueprint


@pytest.fixture
def app():
    sanic_app = Sanic('test')
    sanic_app.blueprint(dummy_user_ws_blueprint)
    return sanic_app


@pytest.mark.asyncio
async def test_login_user_backend_no_body(app):
    request, response = await app.asgi_client.post('/user/login/invalid')
    assert response.status == 401


@pytest.mark.asyncio
async def test_login_user_backend_success(app):
    data = {
        'password': 'opencast'
    }
    request, response = await app.asgi_client.post('/user/login/admin', data=data)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('username') == 'admin'


@pytest.mark.asyncio
async def test_get_user_courses(app):
    request, response = await app.asgi_client.get('/user/anyuser/courses')
    assert response.status == 200
    assert response.content_type == 'application/json'
    course_list = response.json
    assert 1 in course_list
    assert 2 in course_list
    assert 3 in course_list
    assert 4 in course_list
