#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Any

from sanic import Sanic


@lru_cache(maxsize=32)
def format_env_name(env_name: str):
    import re
    return re.sub('[^a-zA-Z0-9]', '_', env_name.upper())


def get_config(app: Sanic, env_name: str, default: Any = None):
    config_key = format_env_name(env_name)
    return app.config.get(config_key, default)
