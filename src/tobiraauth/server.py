#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic
from sanic.response import text

from tobiraauth.utils import format_env_name


def create_app(app_name: str = 'tobira-auth'):
    """Creates Sanic webservice app.

    Register all endpoints respecting configuration.

    :param app_name: The app name. It will also be used as configuration prefix (in UPPER_CASE).
    :return: Sanic app.
    """
    app = Sanic(app_name, env_prefix=f'{format_env_name(app_name)}_')
    register_blueprints(app)

    @app.get('/')
    async def index(request):
        """The index page.

        This endpoint can be used for testing purpose."""
        return text('This is the Tobira-Auth callback service endpoint.')

    # Initialize documentation.
    app.ext.openapi.describe(
        title='Tobira-Auth callback service',
        description='Provide auth or login callback service for Tobira authentication system.',
        version='1.0')
    return app


def register_blueprints(app: Sanic):
    """Register application endpoints.

    Based on application configuration some endpoints (Blueprints) should be enabled or disabled on startup."""
    @app.before_server_start
    async def registration(app):
        if app.config.get('ENABLE_AUTH_CALLBACK', False):
            from tobiraauth.auth_callback import auth_callback_bp
            app.blueprint(auth_callback_bp)
        if app.config.get('ENABLE_LOGIN_CALLBACK', False):
            from tobiraauth.login_callback import login_callback_bp
            app.blueprint(login_callback_bp)
        if app.config.get('ENABLE_DUMMY_USER_SERVICE', False):
            from tobiraauth.dummy_user_webservices import dummy_user_ws_blueprint
            app.blueprint(dummy_user_ws_blueprint)
