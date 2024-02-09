#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

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
    """Tobira-Auth login callback endpoint

    Allways returns a json with `outcome` filed. If its value is `no-user`,
    the userid field is missing in the request or the password is invalid.
    Otherwise, the `outcome` value is `user` and additional fields describe the user metadata.
    The fields are:

    - `username`: The username
    - `displaName`: The users full name to show it in Tobira.
    - `email`: The users email address
    - `roles`: List of user roles based on additional metadata like courses, the user belongs to.

    :param request: The request
    :return: Tobira-Auth callback json.
    """
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
    """Login the user.

    The username and password will be checked, by an external webservice in this example.
    All user metadata including the user roles will be returned as Tobira-Auth callback json.
    On invalid username or password, the `outcome` value will be set to `no-user`.
    For performance reason, the result will be cached a limited amount of time.

    :param request: The request
    :param username: The username
    :param password:  Users password
    :return: Tobira-Auth callback dict
    """
    result = {'outcome': 'no-user'}
    if not username or not password:
        return result
    # === Custom part begins here ===
    # Check the username and password against an external webservice.
    # On success, get the user roles.
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
            logger.debug(f'login_user: User credentials check for {username} failed. '
                         f'Status: {response.status_code}.')
            return result
        userdata = response.json()
    if not userdata or 'username' not in userdata or 'email' not in userdata:
        return result
    user_role = f'ROLE_USER_{re.sub("[^a-zA-Z0-9]", '_', username.strip()).upper()}'
    roles = await get_user_roles(request, username)
    result = {
      'outcome': 'user',
      'username': username,
      'displayName': f'{userdata.get("given_name")} {userdata.get("sur_name")}',
      'email': userdata.get('email'),
      'userRole': user_role,
      'roles': roles,
    }
    # === Custom part ends here ===
    return result
