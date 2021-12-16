"""
Comet Utilities functions are stored here, to be able to download the registry model from COMET.ML correcly
"""
import os
from app import predict
from comet_ml import API
from comet_ml import Experiment
import sklearn

"""
get the comet model centralised command
check if you need to download it first and then return it
"""
def get_comet_model(model_name,model_path,download,workspace="morph-e", model_version=None):
    api = API(api_key = os.environ.get('COMET_API_KEY'))
    # download the model if download = true
    if download==True:
        api.download_registry_model(workspace=workspace, registry_name=model_name, version=model_version,
            output_path=model_path, expand=True, stage=None)
    
    #rename the model
    details =  api.get_registry_model_details(workspace=workspace, registry_name=model_name)
    file_name = details['versions'][0]['assets'][0]['fileName'] 
    os.rename(model_path+file_name,
          model_path+ model_name + ".pkl")
    
    

    

