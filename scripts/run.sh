#!/usr/bin/env bash

# Project path.
PROJECT_PATH="$(readlink -f $(dirname $(readlink -f $0))/..)"
# Path to the configuration environment file.
ENV_FILE="${PROJECT_PATH}/conf/tobira-auth.env"
# Path to the python virtual environment (venv).
# Skip venv activation if empty.
VENV_PATH="${PROJECT_PATH}/venv"

# load configuration from environment file
set -a
. "$ENV_FILE"
set +a
# activate python environment
[ -n ${VENV_PATH} ] && . "${VENV_PATH}/bin/activate"
# run app
PYTHONPATH="${PROJECT_PATH}/src" sanic tobiraauth.server:create_app $*