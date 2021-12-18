import json
from pandas.core.frame import DataFrame
import requests
import pandas as pd
import logging
from ift6758.features.feature_engineering_game import GameData

logger = logging.getLogger(__name__)


class GameClient:
    def __init__(self):
        logger.info(f"Initializing gaming client")
    def ping_game(self,game_id: str,non_processed_event: int=0) -> tuple[pd.DataFrame,int]:
        """
        gameId: Features engineering 2 (milestone 2) DF of the game
        non_processed_event: events or shots that took place >= this event are returned
        """
        game_data = GameData(gameId=game_id)
        df_game,last_event_id = game_data.get_features_2()
        df_game_filtered = df_game.loc[df_game["eventId"]>=non_processed_event]
        return df_game_filtered,last_event_id+1
