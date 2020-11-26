#!/bin/bash

# This script executes the different python modules in charge of fetching the last
# code version and train/test/deploy the defined model.

# Check if we have a new version and clone the repo if that is the case.
cd /framework
python3 src/checkout.py
VALID=$?

if [[ $VALID = 0 ]];
then
    # If we have a new version, kill the previous API process
    kill $(ps aux | grep '[u]vicorn api' | awk '{print $2}')
    # Install the new model dependencies
    cd src/model
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    # Install the API dependencies
    pip install fastapi==0.61.1
    pip install uvicorn==0.12.2
    pip install Jinja2==2.11.2
    pip install aiofiles==0.6.0
    # Copy the required framework files (config file, train/test framework and API files)
    cp ../cicd.py .
    cp ../config.py .
    cp ../api/api.py .
    cp -r ../api/api_templates .
    cp -r ../api/static .
    # Train and evaluate model
    python3 cicd.py
    if [[ $? = 0 ]];
    then
        # Start the API if the deployment was succesful
        uvicorn api:app --host 0.0.0.0 --port 80
    fi
    deactivate
fi