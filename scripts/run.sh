#!/usr/bin/env bash

# This start script will activate python environment from venv folder
# and read environment variables from src/tobiraauth/conf/tobira-auth-callback-service.env file.
# Then the project will be started. All passed arguments will be passed
# through to the process.

# Project path.
PROJECT_PATH="$(readlink -f $(dirname $(readlink -f $0))/..)"
# Path to the configuration environment file.
ENV_FILE="${PROJECT_PATH}/src/tobiraauth/conf/tobira-auth-callback-service.env"
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