from IPython.core.display import display
from ipywidgets import widgets, interact, RadioButtons, IntSlider, Output, Layout, Dropdown

import json
import pandas as pd
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns

import requests
import json
import logging
from ift6758.ift6758.client  import ServingClient,GameClient, serving_client
import collections
import json
import joblib
import pandas as pd
logger = logging.getLogger(__name__)



class DisplayClient():
    def __init__(self,ip: str = "127.0.0.1",port: int = 5000):
        logger.info(f"Initializing display client")
        #CHOOSE WORKSPACE
        workspace_list = ["morph-e"]
        self.workspace_selector = Dropdown(
            options=workspace_list,
            value=workspace_list[0],
            description='Workspace : ',
            disabled=False,
            continuous_update=False,
            layout=Layout(width='50%')
        )

        #CHOOSE Model
        model_list = ["xgbase-bayestuning", "xgbcv-fold-0"]
        self.model_selector = Dropdown(
            options=model_list,
            value=model_list[0],
            description='Model : ',
            disabled=False,
            continuous_update=False,
            layout=Layout(width='50%')
        )

        #CHOOSE Version
        version_list = ["1.0.0"]
        self.version_selector = Dropdown(
            options=version_list,
            value=version_list[0],
            description='Version : ',
            disabled=False,
            continuous_update=False,
            layout=Layout(width='50%')
        )

        #download model
        self.model_button = widgets.Button(description="Get Model",
                                    layout=Layout(width='20%'))

        self.gameid_selector = widgets.Text(
            value='2021020329',
            placeholder='Type a valid Game ID',
            description='Game ID : ',
            disabled=False
        )

        self.game_button = widgets.Button(description="Predict",
                                    layout=Layout(width='20%'))


        self.container_1 = widgets.VBox(children=[self.workspace_selector, self.model_selector, self.version_selector, self.model_button])
        self.container_2 = widgets.VBox(children=[self.gameid_selector, self.game_button])
        self.output = widgets.Output()
        ### Logic and Calculation
        self.game_non_processed_event = 0
        self.gc = GameClient()
        self.sc = ServingClient(ip=ip,port=port)
        self.prev_game_id = 0
        self.xGHome = 0
        self.xGAway = 0
        

    def on_model_button_clicked(self,b):
        """
        On clicking button, Model gets downloaded or raises an exception when version not found
        """
        workspace = self.workspace_selector.value
        model = self.model_selector.value
        version = self.version_selector.value
        ### model prediction then to print 
        with self.output:
            #clear previous output
            self.output.clear_output()
            try:
                model_request=self.sc.download_registry_model(workspace=workspace,model=model,version=version)
                model_dict = model_request.json()
                print(model_dict)
                if model_dict["new_classifier"]=="xgbcv-fold-0":
                    features = ['gameSeconds','totalGameSeconds','timeFromLastEvent','gamePeriod','shotType', 'shotAngle','isHome','coordinatesX','coordinatesY', 'shotDistance','lastEventType','lastEventCoordinatesX','lastEventCoordinatesY','distanceFromLastEvent', 'rebound','speed','changeInShotAngle']
                elif model_dict["new_classifier"]=="xgbase-bayestuning":
                    features = ['gameSeconds','totalGameSeconds','timeFromLastEvent','gamePeriod','shotType', 'shotAngle','isHome','coordinatesX','coordinatesY', 'shotDistance','lastEventType','lastEventCoordinatesX','lastEventCoordinatesY','distanceFromLastEvent', 'rebound','speed','changeInShotAngle']
                self.sc.update_features(features)   
                self.game_non_processed_event = 0
                self.prev_game_id = 0
                self.xGHome = 0
                self.xGAway = 0
            except Exception as e:
                print(f"Exception {e}")


    def on_game_button_clicked(self,b):
        gameid = self.gameid_selector.value
        if self.prev_game_id != gameid:
            self.prev_game_id = gameid
            self.xGHome = 0
            self.xGAway = 0
            self.game_non_processed_event = 0
        try:
            X,last_event,homeaway=self.gc.ping_game(gameid,non_processed_event=self.game_non_processed_event)
            self.exception = ""
            if X.shape[0]>0:
                y=self.sc.predict(X)
                X["xG"] = y["probaIsGoal"]
                X = X[ ['xG'] + [ col for col in X.columns if col != 'xG' ] ]

                self.xGHome += X[X["isHome"]==True]["xG"].sum()
                self.xGAway += X[X["isHome"]==False]["xG"].sum()
                self.game_non_processed_event = last_event.name +1
        except Exception as e:
            self.exception = f"Exception {e}"
        
        ### model prediction then to print 
        with self.output:
            #clear previous output
            self.output.clear_output()
            

            #get results and print table
            print("Game Id is :",gameid)
            if self.exception != "":
                print(self.exception)
                return
            

            
            # fill from model
            period = last_event["about.period"]
            time_left = last_event["about.periodTimeRemaining"]
            home_team = homeaway["home"]
            away_team =  homeaway["away"]
            xg_home = self.xGHome
            xg_away = self.xGAway
            
            #draw table
            table = [[f'PERIOD {period}' , f'TIME LEFT {time_left}'],
                    ["HOME TEAM", "AWAY TEAM"],
                    [home_team, away_team],
                    [xg_home, xg_away]
                ]
            print('                                         ')
            print(tabulate(table, tablefmt='fancy_grid',headers="firstrow", numalign="center", stralign="center"))
            # pd.set_option("display.max_columns",None)
            if X.shape[0]==0:
                print(f"No Shots Taken after last ping")
            display(X)
            self.Xresult = X
