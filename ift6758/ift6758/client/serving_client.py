import json
import requests
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "127.0.0.1", port: int = 5000, features=None):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if features is None:
            features = ["shotDistance", "shotAngle"]
        self.features = features

        # any other potential initialization

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """
        url = self.base_url + '/predict'
        X_model = X[self.features]
        out_json = requests.post(url, 
            json=json.loads(X_model.to_json())
        )
        logger.info("Requested Predictions")
        preds_json =json.loads(out_json.json())
        # y_preds = preds_json.values()
        Y_preds =pd.DataFrame.from_dict(preds_json)

        return Y_preds
        raise NotImplementedError("TODO: implement this function")

    def logs(self) -> dict:
        """Get server logs"""

        url = self.base_url + '/logs'
        logger.info("Requested Logs")
        out_json = requests.get(url)
        print(out_json.text)
        return out_json.text

    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """

        url = self.base_url + '/download_registry_model'
        logger.info("Requested Model Swap")
        requests_json = {
            "workspace": workspace,
            "model": model,
            "version": version,
        }
        out_json = requests.post(url,json=requests_json)
        # print(out_json)
        return out_json

