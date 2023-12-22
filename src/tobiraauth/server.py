#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic

from tobiraauth.auth_callback import auth_callback_bp
from tobiraauth.dummy_user_webservices import dummy_user_ws_blueprint
from tobiraauth.login_callback import login_callback_bp
from tobiraauth.utils import format_env_name


def create_app(app_name: str = 'tobira-auth'):
    app = Sanic(app_name, env_prefix=f'{format_env_name(app_name)}_')
    app.blueprint(auth_callback_bp)
    app.blueprint(login_callback_bp)
    app.blueprint(dummy_user_ws_blueprint)
    return app
