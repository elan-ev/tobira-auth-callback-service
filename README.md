# Tobira-Auth callback service

Tobira provides multiple authentication and authorization mechanisms.
This project is a sample implementation of the `auth-callback` and `login-callback` webservice.
It must be extended by the business logic for your needs.
***DO NOT USE IT IN PRODUCTION WITHOUT REVIEW!***

## How to run
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
# Check configuration in conf/tobira-auth.env
# Run project
sh scripts/run.sh
```

In production, you may run this project as Systemd service. 
The service file template is located [here](./scripts/tobira-auth.service).
