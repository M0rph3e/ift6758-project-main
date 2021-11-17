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
        season_types = [ "02", "03"]
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
    def periodInfo(self):
        DIRECTORY  = f"{self.file_path}/PICKLE/"
        PATH = f"{DIRECTORY}/{self.year}_period_info.pkl"
        if os.path.isfile(PATH):
            print(f"File already Exists, loading from {PATH}")
            df_tot = pd.read_pickle(PATH)
            
        else:
            ## Reference on how to use json_normalize: https://pandas.pydata.org/pandas-docs/version/1.2.0/reference/api/pandas.json_normalize.html
            data = self.get_season_data()
            df_init = pd.json_normalize(data,record_path=[['liveData','linescore','periods']],meta=['gamePk',['gameData','teams','away','name'],['gameData','teams','home','name']])
            home_columns= ['periodType', 'startTime', 'endTime', 'num', 'ordinalNum', 'home.goals','home.shotsOnGoal', 'home.rinkSide', 'gamePk', 'gameData.teams.home.name']
            away_columns= ['periodType', 'startTime', 'endTime', 'num', 'ordinalNum', 'away.goals','away.shotsOnGoal', 'away.rinkSide', 'gamePk', 'gameData.teams.away.name']
            common_columns = ['periodType', 'startTime', 'endTime', 'num', 'ordinalNum', 'goals', 'shotsOnGoal', 'rinkSide', 'gamePk', 'teamname']
            df_home = df_init[home_columns].rename(columns=dict(zip(home_columns,common_columns)))
            df_home["isHomeTeam"]=True

            df_away = df_init[away_columns].rename(columns=dict(zip(away_columns,common_columns)))
            df_away["isHomeTeam"]=False
            df_tot = pd.concat([df_home,df_away])
            df_tot["goalCoordinates"]=df_tot.apply(lambda r: (-89,0) if r['rinkSide']=='right' else (89,0),axis=1)
            df_tot = df_tot.reset_index(drop=True)
            df_tot.to_pickle(PATH)

        return df_tot


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

    def clean_data_all_events(self):

        DIRECTORY  = f"{self.file_path}/PICKLE/"
        PATH = f"{DIRECTORY}/{self.year}_clean_all_events.pkl"

        if os.path.isfile(PATH):
            print(f"File with all events already Exists, loading from {PATH}")
            df_clean = pd.read_pickle(PATH)
            
        else:
            ## Reference on how to use json_normalize: https://pandas.pydata.org/pandas-docs/version/1.2.0/reference/api/pandas.json_normalize.html
            data = self.get_season_data()

            df_init = pd.json_normalize(data,record_path=['liveData','plays','allPlays'],meta=['gamePk'])
            #removed player
            select_columns = ["result.event","gamePk","team.name","about.period","about.periodTime","about.periodType","about.periodTimeRemaining","coordinates.x","coordinates.y","result.secondaryType","result.emptyNet","result.strength.name"]
            df_sel = df_init[select_columns]
            # take all
            df_clean = df_sel.reset_index(drop=True)
            df_clean.to_pickle(PATH)
            print(f"Saved new pickle with all events in {PATH}")

        return df_clean