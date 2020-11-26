# API for a deployed model. It enables to access the model's predict method and get
# information about the model. This API is specific for a time series model.
import subprocess
import os
import importlib
import pickle
import json
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import config as cfg

app = FastAPI()
templates = Jinja2Templates(directory="api_templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Display information about the deployed model
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Check if the model is correctly deployed
    model_deployed, stats = _model_deployed()
    # Model not deployed
    if not model_deployed:
        return {"Error": "Model not deployed"}

    # Display the information page
    return templates.TemplateResponse("base_deployed.html", {"request": request, "test_score": stats["test_score"],"model_info": stats["model_info"]})

# Display the predict page. The user is able to introduce the features to the model and
# retrieve the predictions
@app.get("/predict", response_class=HTMLResponse)
async def predict(request: Request, num_days: int = None):
    # Check if the model is correctly deployed
    model_deployed = _model_deployed()
    # Model not deployed
    if not model_deployed:
        return {"Error": "Model not deployed"}

    # Display an empty predict page if no prediction was required
    if num_days is None:
        return templates.TemplateResponse("predict.html", {"request": request})
    
    # If a prediction was required, compute it
    if num_days <= 0:
        return {"Error": "Number of days to predict must be greater than 0."}
    
    # Import the model package and load the model pickle
    model_framework = importlib.import_module(cfg.MODEL_MODULE)
    model_pickle = None
    with open(cfg.MODEL_NAME + ".pickle", 'rb') as f:
        model_pickle = f.read() 

    # Compute the predictions
    try:
        predictions_raw = model_framework.entry_point.predict(model_pickle, num_days)
    except Exception as e:
        print(e)
        return {"Error": e}

    # As it is a time series, we expect the output to have the dates zipped
    dates = [i.strftime("%m/%d/%Y") for i, j in predictions_raw]
    predictions = [j for i, j in predictions_raw]

    # Display the predict page
    return templates.TemplateResponse("predict.html", {"request": request, "predictions": predictions, "dates": dates})

# Checks if the Model Stats file exists and the model is deployed
def _model_deployed():
        deployed = os.path.isfile(cfg.STATS_FILE)
        if deployed:
            with open(cfg.STATS_FILE, 'r') as f:
                stats = json.load(f)
                deployed &= "deployed" in stats and stats["deployed"] == "Y"
        
        return deployed, stats