#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from cache import AsyncTTL
from httpx import AsyncClient
from sanic import Request
from sanic.log import logger
from tobiraauth.config import ConfigConstants
from tobiraauth.utils import get_config, is_admin, is_admin_mail


def get_user_role(username: str) -> str:
    """Generate user role by replacing special characters in username by '_',
    make it upper case and prefix with 'ROLE_USER_'. If username is empty, return empty string.

    :param username: The username to get user role for
    :return: Users role
    """
    if not username:
        return ''
    return f'ROLE_USER_{re.sub("[^a-zA-Z0-9]", "_", username.strip()).upper()}'


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
