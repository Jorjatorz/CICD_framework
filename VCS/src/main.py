# API to simulate a Webhook event from the desired Version Control System (e.g. Github)
# Call the endpoint '/checkout' to make the system fetch the last pull requests from the
# specified repo and store the pull requests inside the database. All this is performed
# with Singer.io
# See the Readme for learn how to configure the end-points
import subprocess

from fastapi import FastAPI

app = FastAPI()

# Path to start the sync process of the VCS pull requests with our DB
@app.get("/checkout")
async def root():
    command = "/bin/bash fetchGit.sh"
    process = subprocess.run(command.split())

    return {"Result": "Pull requests succesfully fetched" if process.returncode == 0 else "Error while fetching pull requests: {}".format(process.stderr)}
