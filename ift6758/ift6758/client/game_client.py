import json
from pandas.core.arrays import categorical
from pandas.core.frame import DataFrame
import requests
import pandas as pd
import logging
from ift6758.features.feature_engineering_game import GameData
import numpy as np
logger = logging.getLogger(__name__)


class GameClient:
    def __init__(self):
        logger.info(f"Initializing gaming client")
    def ping_game(self,game_id: int,non_processed_event: int=0):
        """
        gameId: Features engineering 2 (milestone 2) DF of the game
        non_processed_event: events or shots that took place >= this event are returned
        """
        game_data = GameData(gameId=game_id)
        home_away = game_data.getHomeAway()
        df_game,last_event = game_data.get_features_2()
        df_game_filtered = df_game.loc[df_game["eventId"]>=non_processed_event]
        

        categories = ['shotType','gamePeriod','lastEventType','rebound','isHome']
        shotType_categories = ['Backhand', 'Deflected', 'Slap Shot', 'Snap Shot', 'Tip-In', 'Wrap-around', 'Wrist Shot']
        gamePeriod_categories  = [1,2,3,4,5]
        lastEventType_categories = ['Blocked Shot', 'Faceoff', 'Game Official', 'Giveaway', 'Goal', 'Hit','Missed Shot', 'Official Challenge', 'Penalty', 'Period End','Period Official', 'Period Ready', 'Period Start', 'Shootout Complete','Shot', 'Stoppage', 'Takeaway']
        rebound_categories= [False, True]
        isHome_categories = [False, True]
        categories_dict = dict(zip(['shotType','gamePeriod','lastEventType','rebound','isHome'],[shotType_categories,gamePeriod_categories,lastEventType_categories,rebound_categories,isHome_categories]))
        for category in categories:
            df_game_filtered[category] = pd.Categorical(df_game_filtered[category],categories =categories_dict[category] )
        # df_game_filtered[categories]=df_game_filtered[categories].astype("category")
        df_game_filtered.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_game_filtered.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_game_filtered["changeInShotAngle"].replace(0,np.nan,inplace=True)
        return df_game_filtered,last_event,home_away
