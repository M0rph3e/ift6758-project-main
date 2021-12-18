from  ift6758.data.data_acquisition import Season
import pandas as pd
import numpy as np
import ift6758.features.utilities as utilities
import os
import requests
## This file is made by combing the functions of other files written in previous milestones. 
class GameData:
    def __init__(self, gameId):
        """
        param gameId : gameId
        """
        self.gameId = gameId
    def periodInfo(self,data):
        ## Reference on how to use json_normalize: https://pandas.pydata.org/pandas-docs/version/1.2.0/reference/api/pandas.json_normalize.html
        df_init = pd.json_normalize(data,record_path=[['liveData','linescore','periods']],meta=['gamePk',['gameData','teams','away','name'],['gameData','teams','home','name']])
        home_columns= ['periodType', 'startTime', 'endTime', 'num', 'ordinalNum', 'home.goals','home.shotsOnGoal', 'home.rinkSide', 'gamePk', 'gameData.teams.home.name']
        away_columns= ['periodType', 'startTime', 'endTime', 'num', 'ordinalNum', 'away.goals','away.shotsOnGoal', 'away.rinkSide', 'gamePk', 'gameData.teams.away.name']
        common_columns = ['periodType', 'startTime', 'endTime', 'num', 'ordinalNum', 'goals', 'shotsOnGoal', 'rinkSide', 'gamePk', 'teamname']
        df_home = df_init[home_columns].rename(columns=dict(zip(home_columns,common_columns)))
        df_home["isHomeTeam"]=True

        df_away = df_init[away_columns].rename(columns=dict(zip(away_columns,common_columns)))
        df_away["isHomeTeam"]=False
        df_tot = pd.concat([df_home,df_away])
        df_tot["goalCoordinates"]=df_tot.apply(lambda r: (-89,0) if r['rinkSide']=='right' else ((89,0) if r['rinkSide']=='left'  else np.nan),axis=1)
        df_tot = df_tot.reset_index(drop=True)

        return df_tot
    
    def clean_data_all_events(self,data):

        df_init = pd.json_normalize(data,record_path=['liveData','plays','allPlays'],meta=['gamePk'])
        select_columns = ["result.event", "result.penaltySeverity", "result.penaltyMinutes","gamePk","team.name","about.period","about.periodTime","about.periodType","about.periodTimeRemaining","coordinates.x","coordinates.y","result.secondaryType","result.emptyNet","result.strength.name"]
        df_sel = df_init[select_columns]
        # take all
        df_clean = df_sel.reset_index(drop=True)

        return df_clean

    def combine_season_periods(self):
        """
        Combine Seasons Info with their periods to get goal coordinates.
        Correct goal coordinates incase they are not existing (Means they are overtime shootouts)
        Can get extra features from periods df as well

        rtype : Pandas DataFrame
        return : The DataFrame With the infos

        @Author : Sai Kalyan (took by Yassir Mamouni for his branch)
        """
        def correctionCoordinates(r):
            if isinstance(r["goalCoordinates"], tuple):
                return r["goalCoordinates"]
            else:
                if r["coordinates.x"]>0:
                    return (89,0)
                else:
                    return (-89,0)
        
        r = requests.get(f"https://statsapi.web.nhl.com/api/v1/game/{self.gameId}/feed/live/")
        if r.status_code == 200:
            game_dict = r.json()
        else:
            return
        df_seasons = self.clean_data_all_events(game_dict)
        df_periods = self.periodInfo(game_dict)
        map_columns = {"periodType": "about.periodType", "num": "about.period","teamname":"team.name","isHomeTeam":"isHome"}
        df_periods_to_join = df_periods[list(map_columns.keys())+["gamePk","goalCoordinates"]].rename(columns=map_columns)
        df_seasons_periods = df_seasons.merge(df_periods_to_join, how='left',on=["about.periodType","about.period","team.name","gamePk"])
        df_seasons_periods["goalCoordinates"] = df_seasons_periods.apply(lambda r: correctionCoordinates(r),axis=1)

        return df_seasons_periods


    def get_features_2(self):
        """
        Getting df with all the features [isGoal,distanceNet,angleNet,emptynet]
        type : Pandas DataFrame
        return : The DataFrame With the basic feature for FE II (4 of Milestone 2)  and last_event_id
        """
        def time_played(row):
            """
            return time in seconds
            """
            if row['about.period']>3:
                ## Overtime is 5 mins and It can go till Shootouts
                time_secs = 3600 + (row['about.period']-4)*300 + row['gameSeconds']
                return time_secs
            else:
                time_secs =  (row['about.period']-1)*1200 + row['gameSeconds']
                return time_secs
        df_seasons_periods = self.combine_season_periods()
        #GameSeconds
        df_seasons_periods['gameSeconds'] = pd.to_timedelta('00:' + df_seasons_periods['about.periodTime'].astype(str)) #concat '00:' to have the format 'hh:mm:ss'
        df_seasons_periods['gameSeconds'] = df_seasons_periods['gameSeconds'].dt.total_seconds()
        df_seasons_periods["totalGameSeconds"] = df_seasons_periods[["gameSeconds","about.period"]].apply(lambda r: time_played(r),axis=1)

        #We already have Game Period, Coordinates, Shot Type,
        df_seasons_periods["result.emptyNet"] = df_seasons_periods["result.emptyNet"].fillna(0)
        df_seasons_periods["distanceNet"]= df_seasons_periods[['coordinates.x','coordinates.y','goalCoordinates']].apply(lambda r: utilities.distance(r["goalCoordinates"],(r["coordinates.x"],r["coordinates.y"])), axis=1)
        df_seasons_periods["angleNet"]= df_seasons_periods[['coordinates.x','coordinates.y','goalCoordinates']].apply(lambda r: utilities.angle(r["goalCoordinates"],(r["coordinates.x"],r["coordinates.y"])), axis=1)
        df_seasons_periods["isGoal"] =df_seasons_periods[["result.event"]].apply(lambda r: 1 if (r["result.event"]=="Goal") else 0,axis=1) ## Add ISGOAL
        #df_seasons_periods.dropna(subset=['coordinates.x','coordinates.y'],inplace=True) ## Sometimes X-cooridnates and Y-cordinates are Nans removing them, need to understand why they are mssing later

        ###################################
        ### ALA's PART: last event features
        ###################################

        df = df_seasons_periods
    
        #shift all relevant info by one to have the last event information
        # keep the gamePK id and the period for a sanity check
        #this is to prevent leaking between games/periods
        df['last.event.gamePk'] = df['gamePk'].shift(1)
        df['last.event.about.period'] = df['about.period'].shift(1)
        df['lastEventType'] = df['result.event'].shift(1)
        df['last.event.about.periodTime'] = df['about.periodTime'].shift(1)
        df['last.event.coordinates.x'] = df['coordinates.x'].shift(1)
        df['last.event.coordinates.y'] = df['coordinates.y'].shift(1)
        ##
        df['last.event.angleNet'] = df['angleNet'].shift(1)
        
        mask = ((df["result.event"]=="Shot") | (df["result.event"]=="Goal")) & (df['last.event.gamePk'] == df['gamePk']) & (df['last.event.about.period'] == df['about.period'])
        df_masked = df.loc[mask]
        
        #Calculate time between this event and last event in seconds
        df_masked.loc[:,'timeFromLastEvent'] = pd.to_datetime(df_masked['about.periodTime'], format='%M:%S') - pd.to_datetime(df_masked['last.event.about.periodTime'], format='%M:%S')
       
        #Calculate distance between this event and last event in feet
        df_masked.loc[:,'distanceFromLastEvent'] = df_masked.apply(
            lambda row: np.linalg.norm(np.array([row['last.event.coordinates.x'], row['last.event.coordinates.y']])-np.array([row['coordinates.x'], row['coordinates.y']])),
            axis=1)
        
        #add rebound if last event is shot
        df_masked.loc[:,'Rebound'] = np.where(df_masked.loc[:,'lastEventType']=='Shot', True, False)
        
        #convert timeFromLastEvent column to seconds
        df_masked.loc[:,'timeFromLastEvent'] = df_masked.loc[:,'timeFromLastEvent'].dt.total_seconds()
        
        #add speed = dist/time
        df_masked.loc[:,'Speed'] = df_masked.loc[:,'distanceFromLastEvent'] / df_masked.loc[:,'timeFromLastEvent']

        #calculate angle difference
        df_masked.loc[:,'changeInShotAngle'] = np.where(df_masked.loc[:,'Rebound']==True, np.abs(df_masked.loc[:,'angleNet']-df_masked.loc[:,'last.event.angleNet']) , 0)

        #Angle Speed
        df_masked.loc[:,'angleSpeed'] = df_masked.loc[:,'changeInShotAngle'] / df_masked.loc[:,'timeFromLastEvent']

        #drop unneeded columns
        df_clean = df_masked.drop(columns=["result.event","about.periodTime","about.periodType","about.periodTimeRemaining","goalCoordinates","last.event.gamePk","last.event.about.period","last.event.about.periodTime","last.event.angleNet","result.strength.name","result.penaltySeverity","result.penaltyMinutes"],axis=1).rename_axis("eventId").reset_index()
        
        df_clean = df_clean.rename({'about.period': 'gamePeriod', 'result.emptyNet': 'emptyNet', 'coordinates.x': 'coordinatesX', 'coordinates.y': 'coordinatesY', 'distanceNet': 'shotDistance', 'angleNet': 'shotAngle', 'result.secondaryType': 'shotType', 'last.event.coordinates.x': 'lastEventCoordinatesX', 'last.event.coordinates.y': 'lastEventCoordinatesY', 'Rebound':'rebound', 'Speed':'speed'}, axis='columns', errors='raise')



        return df_clean,df_seasons_periods.iloc[-1]
