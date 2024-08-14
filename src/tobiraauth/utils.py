#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Any

from sanic import Sanic


@lru_cache(maxsize=32)
def format_env_name(env_name: str) -> str:
    """Format env_name as environment variable.

    Environment variables are upper case and concatenated with underscore.

    :param env_name: string to format as environment variable
    :return: string formatted as environment variable
    """
    import re
    return re.sub('[^a-zA-Z0-9]', '_', env_name.upper())


def get_config(app: Sanic, env_name: str, default: Any = None):
    config_key = format_env_name(env_name)
    return app.config.get(config_key, default)


def is_admin(app: Sanic, username: str) -> bool:
    """Return True, if the username is defined as admin in the config file.

    :app: Sanic app instance
    :username: username to test
    :return: True if the username is defined as admin, False otherwise.
    """
    if getattr(app.ctx, 'admin_users', None) is None:
        admin_users_config = get_config(app=app, env_name='ADMIN_USERS_USERNAME', default=None)
        if admin_users_config is not None:
            if ',' in admin_users_config:
                app.ctx.admin_users = [username.strip() for username in admin_users_config.split(',')
                                       if username.strip() != '']
            else:
                app.ctx.admin_users = [admin_users_config,]
        else:
            app.ctx.admin_users = []
    return username in app.ctx.admin_users


def is_admin_mail(app: Sanic, mail: str) -> bool:
    """Return True, if the email address is defined as admin in the config file.

    :app: Sanic app instance
    :mail: email address to test
    :return: True if the email address is defined as admin, False otherwise.
    """
    if getattr(app.ctx, 'admin_users_mail', None) is None:
        admin_users_mail_config = get_config(app=app, env_name='ADMIN_USERS_MAIL', default=None)
        if admin_users_mail_config is not None:
            if ',' in admin_users_mail_config:
                app.ctx.admin_users_mail = [mail.strip() for mail in admin_users_mail_config.split(',')
                                            if mail.strip() != '']
            else:
                app.ctx.admin_users_mail = [admin_users_mail_config,]
        else:
            app.ctx.admin_users_mail = []
    return mail in app.ctx.admin_users_mail
