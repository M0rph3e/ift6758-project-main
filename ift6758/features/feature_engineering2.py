from  ift6758.data.data_acquisition import Season
import pandas as pd
import numpy as np
import ift6758.features.utilities as utilities
class SeasonDataSetTwo:
    def __init__(self, years):
        """
        param years : array of in : a year seasons
        """
        self.years = years

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
        seasons= []
        periods=[]
        for yr in self.years:
            season = Season(yr,"../ift6758/data")
            df_season = season.clean_data_all_events()
            df_period = season.periodInfo()
            seasons.append(df_season)
            periods.append(df_period)

        df_seasons = pd.concat(seasons).reset_index(drop=True)
        df_periods = pd.concat(periods).reset_index(drop=True)
        map_columns = {"periodType": "about.periodType", "num": "about.period","teamname":"team.name" }
        df_periods_to_join = df_periods[list(map_columns.keys())+["gamePk","goalCoordinates"]].rename(columns=map_columns)
        df_seasons_periods = df_seasons.merge(df_periods_to_join, how='left',on=["about.periodType","about.period","team.name","gamePk"])
        df_seasons_periods["goalCoordinates"] = df_seasons_periods.apply(lambda r: correctionCoordinates(r),axis=1)

        return df_seasons_periods


    def get_features_2(self):
        """
        Getting df with all the features [isGoal,distanceNet,angleNet,emptynet]
        type : Pandas DataFrame
        return : The DataFrame With the basic feature for FE II (4 of Milestone 2) 
        """
        # train_years = [2015,2016,2017,2018]
        df_seasons_periods = self.combine_season_periods()
        #GameSeconds
        df_seasons_periods['gameSeconds'] = pd.to_timedelta('00:' + df_seasons_periods['about.periodTime'].astype(str)) #concat '00:' to have the format 'hh:mm:ss'
        df_seasons_periods['gameSeconds'] = df_seasons_periods['gameSeconds'].dt.total_seconds()
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
        df_masked = df[mask]
        
        #Calculate time between this event and last event in seconds
        df_masked['timeFromLastEvent'] = pd.to_datetime(df_masked['about.periodTime'], format='%M:%S') - pd.to_datetime(df_masked['last.event.about.periodTime'], format='%M:%S')
       
        #Calculate distance between this event and last event in feet
        df_masked['distanceFromLastEvent'] = df_masked.apply(
            lambda row: np.linalg.norm(np.array([row['last.event.coordinates.x'], row['last.event.coordinates.y']])-np.array([row['coordinates.x'], row['coordinates.y']])),
            axis=1)
        
        #add rebound if last event is shot
        df_masked['Rebound'] = np.where(df_masked['lastEventType']=='Shot', True, False)
        
        #convert timeFromLastEvent column to seconds
        df_masked['timeFromLastEvent'] = df_masked['timeFromLastEvent'].dt.total_seconds()
        
        #add speed = dist/time
        df_masked['Speed'] = df_masked['distanceFromLastEvent'] / df_masked['timeFromLastEvent']

        #calculate angle difference
        df_masked['changeInShotAngle'] = np.where(df_masked['Rebound']==True, np.abs(df_masked['angleNet']-df_masked['last.event.angleNet']) , 0)

        #Angle Speed
        df_masked['angleSpeed'] = df_masked['changeInShotAngle'] / df_masked['timeFromLastEvent']

        #drop unneeded columns
        df_clean = df_masked.drop(columns=["result.event","about.periodTime","about.periodType","about.periodTimeRemaining","goalCoordinates","last.event.gamePk","last.event.about.period","last.event.about.periodTime","last.event.angleNet"],axis=1).reset_index(drop=True)
        
        df_clean = df_clean.rename({'about.period': 'gamePeriod', 'result.emptyNet': 'emptyNet', 'coordinates.x': 'coordinatesX', 'coordinates.y': 'coordinatesY', 'distanceNet': 'shotDistance', 'angleNet': 'shotAngle', 'result.secondaryType': 'shotType', 'last.event.coordinates.x': 'lastEventCoordinatesX', 'last.event.coordinates.y': 'lastEventCoordinatesY', 'Rebound':'rebound', 'Speed':'speed'}, axis='columns', errors='raise')

        return df_clean
