"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""
import os
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import sklearn
import pandas as pd
import joblib
from ift6758.comet_utils import get_comet_model

import ift6758


LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
MODELS_DIR = os.environ.get("FLASK_MODELS","downloaded_models/")

global model
global clf
app = Flask(__name__)


@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    global clf,model
    # TODO: setup basic logging configuration
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, filemode='w') #filemode='w' to clear the log file for each run
    app.logger.info('Welcome to the work of Team 11')
    app.logger.info('Initialization')
    # TODO: any other initialization before the first request (e.g. load default model)
    # pass
    default_model = "logreg-distance-angle"
    file_path = f"{MODELS_DIR}/{default_model}.pkl"
    if os.path.isfile(file_path):
        model = default_model
    else:
        model = default_model
        app.logger.info(f"Downloading from COMET {model}")
        get_comet_model(model,MODELS_DIR,download=True,workspace="morph-e")



    clf = joblib.load(file_path)
    app.logger.info(f"Default Classifier Loaded {default_model}")

    # else:




@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    
    # TODO: read the log file specified and return the data
    with open(LOG_FILE,'r') as lf:
        response = lf.read()
    return jsonify(response)  # response must be json serializable!
    raise NotImplementedError("TODO: implement this endpoint")
    response = None
    return jsonify(response)  # response must be json serializable!


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.

    Recommend (but not required) json with the schema:

        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    global clf,model

    # Get POST json data
    json = request.get_json()
    app.logger.info(json)

    # TODO: check to see if the model you are querying for is already downloaded
    model_swap = json["model"]
    workspace = json["workspace"]
    version = json["version"]

    file_model_path = f"{MODELS_DIR}/{model_swap}.pkl"

    if os.path.isfile(file_model_path):
        model = model_swap
        app.logger.info(f"{model} already stored")
    else:
        model = model_swap
        app.logger.info(f"Downloading from COMET {model}")
        get_comet_model(model_swap,MODELS_DIR,download=True,workspace=workspace, model_version=version)


    clf = joblib.load(file_model_path)
    app.logger.info(f"Classifier Swapped with {model}")

        

    # response = {"clf":clf}
    # TODO: if yes, load that model and write to the log about the model change.  
    # eg: app.logger.info(<LOG STRING>)
    
    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the 
    # currently loaded model

    # Tip: you can implement a "CometMLClient" similar to your App client to abstract all of this
    # logic and querying of the CometML servers away to keep it clean here

    # raise NotImplementedError("TODO: implement this endpoint")

    response = {"new_classifier": model_swap}

    app.logger.info(response)
    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """

    # Get POST json data
    json = request.get_json()
    app.logger.info(json)
    X_pred =pd.read_json(json,orient="table")
    y_pred = clf.predict(X_pred)
    y_predproba = clf.predict_proba(X_pred)[:,1]
    X_pred["predictionIsGoal"] = y_pred
    X_pred["probaIsGoal"] = y_predproba
    
    response = X_pred[["probaIsGoal","predictionIsGoal"]].to_json()
    app.logger.info(response)

    return jsonify(response)  # response must be json serializable!

