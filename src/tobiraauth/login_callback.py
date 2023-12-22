#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cache import AsyncTTL
from httpx import AsyncClient
from sanic import Blueprint, Request
from sanic.log import logger
from sanic.response import json, JSONResponse

from tobiraauth.auth_callback import get_user_roles
from tobiraauth.utils import get_config

login_callback_bp = Blueprint('login_callback', url_prefix='/login')


@login_callback_bp.post('/')
async def login_callback(request: Request) -> JSONResponse:
    result = {'outcome': 'no-user'}
    try:
        body = request.json
        username = body.get('userid')
        password = body.get('password')
    except:
        logger.warning(f'login_callback: Unable to read userdata from request.')
        return json(result, status=400)

    if not username or not password:
        return json(result, status=400)

    result = await login_user(request, username, password)
    return json(result, status=200)


@AsyncTTL(time_to_live=300, maxsize=1024, skip_args=1)
async def login_user(request: Request, username: str, password: str) -> dict:
    result = {'outcome': 'no-user'}
    if not username or not password:
        return result
    # === Custom part begins here ===
    user_login_ws_url = get_config(request.app, 'USER_LOGIN_WS_URL', None)
    if not user_login_ws_url:
        return result
    user_login_ws_url = user_login_ws_url.format(username=username)
    params = {
        'password': password
    }
    async with AsyncClient() as http_client:
        response = await http_client.post(user_login_ws_url, data=params)
        if response.is_error:
            logger.debug(f'login_user: Unable to query user courses for {username}. '
                         f'Status: {response.status_code}.')
            return result
        userdata = response.json()
    roles = await get_user_roles(request, username)
    result = {
      'outcome': 'user',
      'username': username,
      'displayName': f'{userdata.get("given_name")} {userdata.get("sur_name")}',
      'email': userdata.get('email'),
      'roles': roles,
    }
    # === Custom part ends here ===
    return result
