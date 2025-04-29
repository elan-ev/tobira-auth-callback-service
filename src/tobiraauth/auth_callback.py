#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Blueprint, Request
from sanic.log import logger
from sanic.response import json, JSONResponse
from tobiraauth.common import get_user_roles, get_user_role

from tobiraauth.config import ConfigConstants
from tobiraauth.utils import get_config

auth_callback_bp = Blueprint('auth_callback', url_prefix='/auth')


@auth_callback_bp.get('/')
async def auth_callback(request: Request) -> JSONResponse:
    """Tobira-Auth auth callback endpoint

    Allways returns a json with `outcome` filed. If its value is `no-user`, the username header is missing.
    Otherwise, the `outcome` value is `user` and additional fields describe the user metadata.
    The fields are:

    - `username`: The username
    - `displayName`: The users full name to show it in Tobira.
    - `email`: The users email address
    - `roles`: List of user roles based on affiliation header and additional metadata like courses, the user belongs to.

    :param request: The request.
    :return: Tobira-Auth callback json.
    """
    username = request.headers.get(
        get_config(request.app, 'username_header', ConfigConstants.USERNAME_HEADER),
        None)

    if username is None:
        return json({'outcome': 'no-user'})

    display_name = request.headers.get(
        get_config(request.app, 'display_name_header', ConfigConstants.DISPLAY_NAME_HEADER),
        None)
    email = request.headers.get(
        get_config(request.app, 'email_header', ConfigConstants.EMAIL_HEADER),
        None)
    home_organization = request.headers.get(
        get_config(request.app, 'home_organization', ConfigConstants.HOME_ORGANIZATION_HEADER),
        None)

    if display_name is None:
        given_name = request.headers.get(
            get_config(request.app, 'given_name_header', ConfigConstants.GIVEN_NAME_HEADER),
            None)
        surname = request.headers.get(
            get_config(request.app, 'surname_header', ConfigConstants.SURNAME_HEADER),
            None)
        if given_name is not None and surname is not None:
            display_name_format = get_config(request.app, 'display_name_format', '{given_name} {surname}')
            display_name = display_name_format.format(given_name=given_name, surname=surname)

    result = {
      'outcome': 'user',
      'username': username,
      'displayName': display_name,
      'email': email,
      'userRole': get_user_role(username),
      'roles': []
    }

    custom_roles = get_config(request.app, 'custom_roles', None)
    if custom_roles is not None:
        for role in custom_roles.split(','):
            role = role.strip()
            if role.strip() != '':
                if '{' in role:
                    result.get('roles').append(role.format(
                        username=username,
                        email=email,
                        home_organization=home_organization,
                    ))
                else:
                    result.get('roles').append(role)
    try:
        user_roles = await get_user_roles(request, username, email)
        if len(result.get('roles')) > 0:
            user_roles.extend(result.get('roles'))
        result['roles'] = list({*user_roles})
    except:
        logger.exception(f'Unable to get user roles for user {username}.')
    return json(result)
