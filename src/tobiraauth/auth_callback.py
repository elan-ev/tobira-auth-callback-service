#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from cache import AsyncTTL
from httpx import AsyncClient
from sanic import Blueprint, Request
from sanic.log import logger
from sanic.response import json, JSONResponse

from tobiraauth.config import ConfigConstants
from tobiraauth.utils import get_config, is_admin, is_admin_mail

auth_callback_bp = Blueprint('auth_callback', url_prefix='/auth')


def get_user_role(username: str) -> str:
    """Generate user role by replacing special characters in username by '_',
    make it upper case and prefix with 'ROLE_USER_'. If username is empty, return empty string.

    :param username: The username to get user role for
    :return: Users role
    """
    if not username:
        return ''
    return f'ROLE_USER_{re.sub("[^a-zA-Z0-9]", "_", username.strip()).upper()}'


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


async def get_user_roles(request: Request, username: str, mail: str = None):
    """Returns a list of user roles for the given user.

    :param request: The request.
    :param username: The username to get the roles for.
    :param mail: The users mail address for admin privileges check.
    :return: User roles list, may be empty.
    """

    roles = [
        'ROLE_ANONYMOUS',
        'ROLE_USER',
        get_user_role(username),
        f'ROLE_AAI_USER_{username.strip()}'
    ]
    user_affiliations_headers = request.headers.getall(
        get_config(request.app, 'affiliation_header', ConfigConstants.AFFILIATION_HEADER),
        [])
    if is_admin(request.app, username) or is_admin_mail(request.app, mail):
        roles += [
            'ROLE_TOBIRA_ADMIN',
            'ROLE_TOBIRA_UPLOAD',
            'ROLE_TOBIRA_STUDIO',
            'ROLE_TOBIRA_EDITOR',
        ]
    else:
        for user_affiliations in user_affiliations_headers:
            for user_affiliation in user_affiliations.split(';'):
                if 'staff' in user_affiliation.strip():
                    roles += [
                        'ROLE_TOBIRA_UPLOAD',
                        'ROLE_TOBIRA_STUDIO',
                        'ROLE_TOBIRA_EDITOR',
                    ]
    try:
        course_roles = await get_user_course_roles(request, username)
        if course_roles and isinstance(course_roles, list):
            roles += course_roles
    except:
        logger.warning(f'Unable to get user course roles for {username}.')
    return roles


@AsyncTTL(time_to_live=300, maxsize=1024, skip_args=1)
async def get_user_course_roles(request: Request, username: str):
    """Get user roles based on course IDs, belongs to the user.

    For performance reasons the result will be cached for a limited amount of time.

    :param request: The request.
    :param username: The username to get the course roles for.
    :return: List of user roles based on course IDs, may be empty.
    """
    logger.debug(f'get_user_course_roles: Query user course roles for {username}.')
    roles = []
    # === Custom part begins here ===
    # Call external endpoint to get the course IDs the user belongs to. For each ID, create a user role.
    user_courses_ws_url = get_config(request.app, 'USER_COURSES_WS_URL', None)
    if not user_courses_ws_url:
        return roles
    user_courses_ws_url = user_courses_ws_url.format(username=username)
    async with AsyncClient() as http_client:
        response = await http_client.get(user_courses_ws_url, follow_redirects=True)
        if response.is_error:
            logger.debug(f'get_user_course_roles: Unable to query user courses for {username}. '
                         f'Status: {response.status_code}.')
            return roles
        user_courses = response.json()
    for course_id in user_courses:
        roles.append(f'ROLE_COURSE_{course_id}_Learner')
    # === Custom part ends here ===
    return roles
