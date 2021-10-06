import pandas as pd
import requests
import os
from tqdm import tqdm
import pickle
import sys

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
        # print("kkk")
        self.data = self.get_season_data(year,file_path)
        # pass        
    def get_season_data(self,year, file_path):
        """
        Get the data from the Hockey API in Pickle format for a specific season (year-year+1) and store them to a given file_path. Pickle contains list[dicts of all games in the season]

        :param year: year of the season (example 2017 will download Season 2017-2018)
        :type year: int
        :param file_path: Directory where the pickle file for entire season is stored are going to be saved
        :type file_path: str

        :rtype: list[dict]
        :return: list[ dicts of all games in the season],

        """
        YEAR = year
        DIRECTORY  = f"{file_path}/PICKLE/"
        PATH = f"{DIRECTORY}/{YEAR}.pkl"
        MAX_GAMES=1300
        os.makedirs(DIRECTORY, exist_ok=True)
        season_types = ["01", "02", "03", "04"]
        games_list = []
        if os.path.isfile(PATH):
            with open(PATH, 'rb') as f:
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
        print(f"Len of games_list in {year} is {len(games_list)}")

        return games_list

    def __str__(self):
        return f"Season of Year {self.year}"    
    def __add__(self,season2):
        """
        Add data of other season and return in form of list of all game dicts.
        :param: season2
        :type: Season object
        :rtype: list[dict]
        :return: list[ dicts of all games in two seasons]
        """
        return self.data + season2.data