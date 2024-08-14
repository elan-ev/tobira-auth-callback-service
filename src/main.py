#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic
from sanic.log import logger
from sanic.worker.loader import AppLoader

from tobiraauth.server import create_app


def main():
    """Project entry point for development.

    After loading the configuration file `tobiraauth/conf/tobira-auth.env`
    the webservice will be started with debug configuration.

    **Do not use it in production.**
    """
    logger.warning('This starting point should only be used during development. '
                   'Please read documentation how to use this project in production.')
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path='tobiraauth/conf/tobira-auth.env')
    except:
        logger.warning(f'Tobira-Auth configuration file not loaded. '
                       f'Do you installed development requirements from requirements-dev.txt?')
    loader = AppLoader(factory=create_app)
    app = loader.load()
    app.prepare(debug=True, single_process=True, auto_reload=False)
    Sanic.serve(primary=app, app_loader=loader)


if __name__ == '__main__':
    main()
