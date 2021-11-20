from  ift6758.data.data_acquisition import Season
import pandas as pd
import os
from  ift6758.data.data_acquisition import Season
import pandas as pd
import ift6758.utilities as utilities
class SeasonDataSet:
    def __init__(self,years) -> None:
        """
        Creates a dataset with features in feature engineering-1
        """
        self.years = years
    def combine_season_periods(self):
        """
        Combine Seasons Info with their periods to get goal coordinates.
        Coorect goal coordinates incase they are not existing (Means they are overtime shootouts)
        Can get extra features from periods df as well
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
            df_season = season.clean_data()
            df_period = season.periodInfo()
            seasons.append(df_season)
            periods.append(df_period)

        df_seasons = pd.concat(seasons).reset_index(drop=True)
        df_periods = pd.concat(periods).reset_index(drop=True)
        map_columns = {"periodType": "about.periodType", "num": "about.period","teamname":"team.name" }
        df_periods_to_join = df_periods[list(map_columns.keys())+["gamePk","goalCoordinates"]].rename(columns=map_columns)
        df_seasons_periods = df_seasons.merge(df_periods_to_join, how='left',on=["about.periodType","about.period","team.name","gamePk"])
        df_seasons_periods["goalCoordinates"] = df_seasons_periods.apply(lambda r: correctionCoordinates(r),axis=1) ## 

        return df_seasons_periods


    def get_tidy_data(self):
        """
        Getting df with all the features [isGoal,distanceNet,angleNet,emptynet]
        """
        # train_years = [2015,2016,2017,2018]
        df_seasons_periods = self.combine_season_periods()
        df_seasons_periods["result.emptyNet"] = df_seasons_periods["result.emptyNet"].fillna(0)
        df_seasons_periods.loc[df_seasons_periods["result.emptyNet"]==False,["result.emptyNet"]]=0
        df_seasons_periods.loc[df_seasons_periods["result.emptyNet"]==True,["result.emptyNet"]]=1

        df_seasons_periods["isGoal"] =df_seasons_periods[["result.event"]].apply(lambda r: 1 if (r["result.event"]=="Goal") else 0,axis=1) ## Add ISGOAL
        df_seasons_periods["distanceNet"]= df_seasons_periods[['coordinates.x','coordinates.y','goalCoordinates']].apply(lambda r: utilities.distance(r["goalCoordinates"],(r["coordinates.x"],r["coordinates.y"])), axis=1)
        df_seasons_periods["angleNet"]= df_seasons_periods[['coordinates.x','coordinates.y','goalCoordinates']].apply(lambda r: utilities.angle(r["goalCoordinates"],(r["coordinates.x"],r["coordinates.y"])), axis=1)
        
        df_seasons_periods.dropna(subset=['coordinates.x','coordinates.y'],inplace=True) ## Sometimes X-cooridnates and Y-cordinates are Nans removing them, need to understand why they are mssing later

        return df_seasons_periods

        





