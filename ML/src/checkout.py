# Module in charge of fetching the last code version from the DB and, in case of
# a newer version, clone the repo and prepare the model for the training, test and deploy process
import json
import shutil
import importlib
import os
import sys

from git import Repo

from pull_request_service import pull_request_checker
from pull_request_service.db_managers.pg_manager import PGManager
import config as cfg

def pipeline():
    # Get the last pull request
    print("Pulling the last Pull Request")
    manager = PGManager() # Use Postgres manager. If the DB changes, change this by the corresponding manager
    last_pr = pull_request_checker.get_last_pull_request(manager)
    manager.close()

    if last_pr is None:
        print("Error pulling the last Pull Request")
        sys.exit(1)
    
    # Get current Model Stats file. This file contains the version of the currently deployed model
    relative_path = os.path.dirname(__file__)
    stats = None
    try:
        with open(os.path.join(relative_path, cfg.MODEL_DIRECTORY, cfg.STATS_FILE)) as stats_file:
            stats = json.load(stats_file)
    except:
        print("No Model Stats file was found")

    print("Checking version diferences")
    # Compare the new version with the current version. Two cases for a new build:
    # 1. The stats file does not exist or is corrupted.
    # 2. The deployed version is older.
    needs_rebuild = False
    new_version = int(last_pr.merge_date.timestamp())
    if stats is None or not "version" in stats:
        needs_rebuild = True
    elif stats["version"] != new_version:
        needs_rebuild = True

    if not needs_rebuild:
        if cfg.ALWAYS_BUILD:
            needs_rebuild = True
        else:
            print("Current model is up to date")
            sys.exit(1)
    
    # Clone the repository
    print("New version! Cloning the repository")
    try:
        # Delete previous model folder
        shutil.rmtree(os.path.join(relative_path, cfg.MODEL_DIRECTORY))
    except:
        pass
    model_dir = os.path.join(relative_path, cfg.MODEL_DIRECTORY)
    Repo.clone_from(cfg.GIT_REPO_URL, model_dir)

    # Set the model version and status in the Model Stats file
    stats = {}
    stats["version"] = new_version
    stats["deployed"] = "N"
    with open(os.path.join(model_dir, cfg.STATS_FILE), 'w') as stats_file:
        json.dump(stats, stats_file)

    sys.exit(0)

if __name__ == "__main__":
    pipeline()