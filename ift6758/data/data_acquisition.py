import pandas as pd
import requests
import os
from tqdm import tqdm
import pickle
import sys
import json
import numpy as np

class Season:
    def __init__(self,year,file_path):
        """
        :param year: year of the season (example 2017 Season 2017-2018)
        :type year: int
        :param file_path: Directory where the pickle file for entire season is stored are going to be saved
        :type file_path: str
        Initialising variables required for the season.
        Calling function get_season_data to load all games of the season in memory and store pickle files(if required)
        """
        self.year = year
        self.file_path = file_path
        # self.data = self.get_season_data(year,file_path)

        # pass        
    def get_season_data(self):
        """
        Get the data from the Hockey API in Pickle format for a specific season (year-year+1) and store them to a given file_path. Pickle contains list[dicts of all games in the season]

        :rtype: list[dict]
        :return: list[ dicts of all games in the season],

        """
        YEAR = self.year
        DIRECTORY  = f"{self.file_path}/PICKLE/"
        PATH = f"{DIRECTORY}/{YEAR}.pkl"
        MAX_GAMES=1300
        os.makedirs(DIRECTORY, exist_ok=True)
        season_types = ["01", "02", "03", "04"]
        games_list = []
        if os.path.isfile(PATH):
            with open(PATH, 'rb') as f:
                print(f"File already Exists, loading from {PATH}")
                games_list = pickle.load(f)

        else:
            for season_type in season_types:
                for g in tqdm(range(1,MAX_GAMES)):
                    game_number = str(g).zfill(4)
                    GAME_ID = f"{YEAR}{season_type}{game_number}"
                    r = requests.get(f"https://statsapi.web.nhl.com/api/v1/game/{GAME_ID}/feed/live/")
                    if r.status_code == 200:
                        ## Storing as dicts
                        game_dict = r.json()
                        games_list.append(game_dict)
            with open(PATH,'wb') as f:
                pickle.dump(games_list,f)
        print(f"Len of games_list in {YEAR} is {len(games_list)}")

        return games_list

    def __str__(self):
        return f"Season of Year {self.year}"    
    # def __add__(self,season2):
    #     """
    #     Add data of other season and return in form of list of all game dicts.
    #     :param: season2
    #     :type: Season object
    #     :rtype: list[dict]
    #     :return: list[ dicts of all games in two seasons]
    #     """
    #     return self.data + season2.data

    def clean_data(self):
        """
        Cleaning data for the data of season. and store it in a pickle file f"{file_path}/PICKLE/{year}_clean.pkl"
        """ 
        def important_players(players):
            """
            :param: players - list of players
            Typical list of players: [{'player': {'id': 8475790, 'fullName': 'Erik Gudbranson', 'link': '/api/v1/people/8475790'}, 'playerType': 'Shooter'}, {'player': {'id': 8471734, 'fullName': 'Jonathan Quick', 'link': '/api/v1/people/8471734'}, 'playerType': 'Goalie'}]
            We return the names of goalie and shooter from list of players
            """
            shooter = np.NaN
            goalie = np.NaN
            for player in players:
                playerType = player.get("playerType", np.NaN)
                if playerType == "Shooter" or playerType== "Scorer":
                    shooter = player["player"].get("fullName", np.NaN)
                elif playerType == "Goalie":
                    goalie = player["player"].get("fullName", np.NaN)
            return shooter,goalie

        DIRECTORY  = f"{self.file_path}/PICKLE/"
        PATH = f"{DIRECTORY}/{self.year}_clean.pkl"
        if os.path.isfile(PATH):
            print(f"File already Exists, loading from {PATH}")
            df_clean = pd.read_pickle(PATH)
            
        else:
            ## Reference on how to use json_normalize: https://pandas.pydata.org/pandas-docs/version/1.2.0/reference/api/pandas.json_normalize.html
            data = self.get_season_data()

            df_init = pd.json_normalize(data,record_path=['liveData','plays','allPlays'],meta=['gamePk'])
            select_columns = ["result.event","gamePk","team.name","players","about.period","about.periodTime","about.periodType","about.periodTimeRemaining","coordinates.x","coordinates.y","result.secondaryType","result.emptyNet","result.strength.name"]
            df_sel = df_init[select_columns]
            df_fil_event=df_sel[(df_sel["result.event"]=="Shot")| (df_sel["result.event"]=="Goal")]
            df_fil_event['shooter'],df_fil_event['goalie'] = zip(*df_fil_event["players"].map(important_players)) ## Choosing Goalie and shooter
            df_clean = df_fil_event.drop(columns=["players"],axis=1).reset_index(drop=True)
            df_clean.to_pickle(PATH)

        return df_clean
