#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sanic import Sanic
from sanic.log import logger
from sanic.worker.loader import AppLoader

from tobiraauth.server import create_app


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path='../conf/tobira-auth.env')
    except:
        logger.warning(f'Tobira-Auth configuration file not loaded. '
                       f'Do you installed development requirements from requirements-dev.txt?')
    loader = AppLoader(factory=create_app)
    app = loader.load()
    app.prepare(debug=True, single_process=True, auto_reload=False)
    Sanic.serve(primary=app, app_loader=loader)


if __name__ == '__main__':
    main()
