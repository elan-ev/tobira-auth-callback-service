# Tobira-Auth callback service

Tobira provides multiple authentication and authorization mechanisms.
This project is a sample implementation of the `auth-callback` and `login-callback` webservice.
It must be extended by the business logic for your needs.
***DO NOT USE IT IN PRODUCTION WITHOUT REVIEW!***

## Python Version
Python ≥ 3.8 is required. Older versions of Python may not work.

## How to start development
First you need python installed on your machine. Then we will create a python virtual environment, 
install all python dependencies and run the project.

```shell
# Create python virtual environment (need only be done once)
python -m venv venv
# Activate python virtual environment 
source venv/bin/activate
# Update python package manager (need only be done once)
pip install --upgrade pip
# Install project dependencies (need only be done once)
pip install -r requirements.txt
# Development dependencies are optional and can be installed with (need only be done once)
pip install -r requirements-dev.txt
```

At this point we have a python virtual environment with all project dependencies installed.
From here you can start develop the customizations for your institution.
To run the project during development you can use a shell script `sh scripts/run.sh`
or use python wrapper directly `PYTHONPATH=src python src/main.py`.
You may want to set some environment variables.
They are listed and documented [here](src/tobiraauth/conf/tobira-auth-callback-service.env).
This configuration file will be loaded by `run.sh` and `main.py`.

## How to run in production

In production, you should run this project as Systemd service.
The installation process is a bit different.
```shell
# Create python virtual environment
python -m venv /opt/tobira-auth-callback-service
# Activate python virtual environment
source /opt/tobira-auth-callback-service/bin/activate
# Install project and dependencies
pip install .
```
At this point you have installed the project into your virtual environment.
The sources aren't needed any more and can be removed.
Next steps are: create Systemd service and install configuraiton.
The service file template is located [here](scripts/tobira-auth-callback-service.service).
The configuration fie is located [here](src/tobiraauth/conf/tobira-auth-callback-service.env).
Please review the configuration file before installing.
Following steps will install the configuration file and Systemd service.
```shell
cp src/tobiraauth/conf/tobira-auth-callback-service.env /etc/default/
cp ./scripts/tobira-auth-callback-service.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now tobira-auth-callback-service.service
```
