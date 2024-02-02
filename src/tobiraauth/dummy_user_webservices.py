#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Blueprint
from sanic.exceptions import Unauthorized
from sanic.log import logger
from sanic.response import json

dummy_user_ws_blueprint = Blueprint('dummy_user_webservices', url_prefix='/user')


# Test endpoints
@dummy_user_ws_blueprint.post('/login/<username:str>')
async def login_user_backend(request, username: str):
    logger.warning(f'You are calling a dummy user service. DO NOT USE IT IN PRODUCTION!!!')
    userdata = request.get_form()
    password = userdata.get('password', None)
    if username == 'admin' and password == 'opencast':
        userdata = {
            'username': username,
            'given_name': 'Admin',
            'sur_name': 'Opencast',
            'email': 'admin@localhost',
        }
        return json(userdata)
    raise Unauthorized()


@dummy_user_ws_blueprint.get('/<username:str>/courses')
async def get_user_courses(request, username: str):
    logger.warning(f'You are calling a dummy user service. DO NOT USE IT IN PRODUCTION!!!')
    return json([1, 2, 3, 4])


@dummy_user_ws_blueprint.after_server_start
async def configure_endpoints(app):
    app.config.update({'USER_LOGIN_WS_URL': 'http://localhost:8000/user/login/{username}'})
    app.config.update({'USER_COURSES_WS_URL': 'http://localhost:8000/user/{username}/courses'})
