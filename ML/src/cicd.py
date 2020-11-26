# This module is in charge of training, testing and deploying the last model's version
# The model must implement the CI/CD interface and call the module 'main.py'
# The training data is static and already stored in the Docker image.
import os
import sys
import json

import pandas as pd

import main
import config as cfg

def exec():
    # Get the model entry point
    model = main.entry_point

    # Train the model using the static training set stored in the container
    # The number of rows loaded has been limited to make the example run faster
    # This number can be modified/removed but the example will require considerably more resource.
    try:
        train = pd.read_csv("../data/train.csv", nrows=5000)
        model_pickle = model.train(train)
    except Exception as e:
        print("Error while training the model")
        print(e)
        sys.exit(1)
    del train

    # Evaluate the model. This uses a static test set stored in the container
    try:
        test = pd.read_csv("../data/test.csv")
        score = model.evaluate(model_pickle, test)
    except Exception as e:
        print("Error while testing the model")
        print(e)
        sys.exit(1)

    # Get Model Stats file
    relative_path = os.path.dirname(__file__)
    stats = None
    try:
        with open(os.path.join(relative_path, cfg.STATS_FILE)) as stats_file:
            stats = json.load(stats_file)
    except Exception as e:
        print("Error while reading the model stats file")
        print(e)
        sys.exit(1)

    # Deploy new model. Save the updated Model Stats file and the model's pickle
    stats["deployed"] = "Y"
    stats = {**stats, "test_score": score, "model_info": model.info()}
    with open(os.path.join(relative_path, cfg.STATS_FILE), 'w') as stats_file:
        json.dump(stats, stats_file)
    with open(cfg.MODEL_NAME + ".pickle", 'wb') as f:
        f.write(model_pickle)

    sys.exit()

if __name__ == "__main__":
    exec()