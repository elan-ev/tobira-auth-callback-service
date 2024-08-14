#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from pytest_httpx import HTTPXMock
from sanic import Sanic

from tobiraauth.auth_callback import auth_callback_bp
from tobiraauth.config import ConfigConstants


@pytest.fixture
def app():
    sanic_app = Sanic('test')
    sanic_app.blueprint(auth_callback_bp)
    sanic_app.config.USER_COURSES_WS_URL = 'http://localhost:4567/user/{username}/courses'
    return sanic_app


@pytest.mark.asyncio
async def test_auth_callback_no_header(app):
    request, response = await app.asgi_client.get('/auth')
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'no-user'


@pytest.mark.asyncio
async def test_auth_callback_username_header(app):
    headers = {
        ConfigConstants.USERNAME_HEADER: 'jane'
    }
    request, response = await app.asgi_client.get('/auth', headers=headers)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == 'jane'
    assert userdata.get('userRole') == 'ROLE_USER_JANE'
    roles = userdata.get('roles')
    assert 'ROLE_ANONYMOUS' in roles
    assert 'ROLE_USER_JANE' in roles
    assert 'ROLE_AAI_USER_jane' in roles
    assert 'ROLE_TOBIRA_EDITOR' not in roles
    assert 'ROLE_TOBIRA_STUDIO' not in roles
    assert 'ROLE_TOBIRA_UPLOAD' not in roles


@pytest.mark.asyncio
async def test_auth_callback_all_headers(app):
    headers = {
        ConfigConstants.USERNAME_HEADER: 'jane@edu.org',
        ConfigConstants.DISPLAY_NAME_HEADER: 'Jane Doe',
        ConfigConstants.EMAIL_HEADER: 'jane.doe@edu.org',
        ConfigConstants.AFFILIATION_HEADER: 'member;staff',
    }
    request, response = await app.asgi_client.get('/auth', headers=headers)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == headers.get(ConfigConstants.USERNAME_HEADER)
    assert userdata.get('displayName') == headers.get(ConfigConstants.DISPLAY_NAME_HEADER)
    assert userdata.get('email') == headers.get(ConfigConstants.EMAIL_HEADER)
    assert userdata.get('userRole') == "ROLE_USER_JANE_EDU_ORG"
    roles = userdata.get('roles')
    assert len(roles) == 7
    assert 'ROLE_ANONYMOUS' in roles
    assert 'ROLE_USER' in roles
    assert 'ROLE_USER_JANE_EDU_ORG' in roles
    assert 'ROLE_AAI_USER_jane@edu.org' in roles
    assert 'ROLE_TOBIRA_EDITOR' in roles
    assert 'ROLE_TOBIRA_STUDIO' in roles
    assert 'ROLE_TOBIRA_UPLOAD' in roles


@pytest.mark.asyncio
async def test_auth_callback_user_courses(app, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method='GET', url='http://localhost:4567/user/jane@edu.org/courses', json=[1, 2, 3, 4])
    headers = {
        ConfigConstants.USERNAME_HEADER: 'jane@edu.org',
    }
    request, response = await app.asgi_client.get('/auth', headers=headers)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == headers.get(ConfigConstants.USERNAME_HEADER)
    roles = userdata.get('roles')
    assert len(roles) == 8
    assert 'ROLE_ANONYMOUS' in roles
    assert 'ROLE_USER' in roles
    assert 'ROLE_USER_JANE_EDU_ORG' in roles
    assert 'ROLE_AAI_USER_jane@edu.org' in roles
    assert 'ROLE_COURSE_1_Learner' in roles
    assert 'ROLE_COURSE_2_Learner' in roles
    assert 'ROLE_COURSE_3_Learner' in roles
    assert 'ROLE_COURSE_4_Learner' in roles


@pytest.mark.asyncio
async def test_auth_callback_is_admin_user(app):
    app.config['ADMIN_USERS_USERNAME'] = 'jane.admin@edu.org, bob@edu.org'
    headers = {
        ConfigConstants.USERNAME_HEADER: 'jane.admin@edu.org',
    }
    request, response = await app.asgi_client.get('/auth', headers=headers)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == headers.get(ConfigConstants.USERNAME_HEADER)
    roles = userdata.get('roles')
    assert 'ROLE_TOBIRA_ADMIN' in roles
    assert 'ROLE_TOBIRA_EDITOR' in roles
    assert 'ROLE_TOBIRA_STUDIO' in roles
    assert 'ROLE_TOBIRA_UPLOAD' in roles


@pytest.mark.asyncio
async def test_auth_callback_is_not_admin_user(app):
    app.config['ADMIN_USERS_USERNAME'] = 'jane.admin@edu.org, bob@edu.org'
    headers = {
        ConfigConstants.USERNAME_HEADER: 'jane.nonadmin@edu.org',
    }
    request, response = await app.asgi_client.get('/auth', headers=headers)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == headers.get(ConfigConstants.USERNAME_HEADER)
    roles = userdata.get('roles')
    assert 'ROLE_TOBIRA_ADMIN' not in roles


@pytest.mark.asyncio
async def test_auth_callback_is_admin_user_mail(app):
    app.config['ADMIN_USERS_MAIL'] = 'jane.admin@edu.org, bob@edu.org'
    headers = {
        ConfigConstants.USERNAME_HEADER: 'jane.admin@edu.org',
        ConfigConstants.EMAIL_HEADER: 'jane.admin@edu.org',
    }
    request, response = await app.asgi_client.get('/auth', headers=headers)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == headers.get(ConfigConstants.USERNAME_HEADER)
    roles = userdata.get('roles')
    assert 'ROLE_TOBIRA_ADMIN' in roles
    assert 'ROLE_TOBIRA_EDITOR' in roles
    assert 'ROLE_TOBIRA_STUDIO' in roles
    assert 'ROLE_TOBIRA_UPLOAD' in roles


@pytest.mark.asyncio
async def test_auth_callback_is_not_admin_user_mail(app):
    app.config['ADMIN_USERS_MAIL'] = 'jane.admin@edu.org, bob@edu.org'
    headers = {
        ConfigConstants.USERNAME_HEADER: 'jane.nonadmin@edu.org',
        ConfigConstants.EMAIL_HEADER: 'jane.nonadmin@edu.org',
    }
    request, response = await app.asgi_client.get('/auth', headers=headers)
    assert response.status == 200
    assert response.content_type == 'application/json'
    userdata = response.json
    assert userdata.get('outcome') == 'user'
    assert userdata.get('username') == headers.get(ConfigConstants.USERNAME_HEADER)
    roles = userdata.get('roles')
    assert 'ROLE_TOBIRA_ADMIN' not in roles
