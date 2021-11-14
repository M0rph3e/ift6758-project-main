import pandas as pd
import os
import pickle
import sys
import numpy as np
import math

class Utilities:
    """
    Utility classs to use standalone functions in the basic data visualization.


    Methods
    ------------
    rink_distance(self,x,y)
        returns the distance from the rink on the stadium depending on the x and y coordinates of the hockey dataframe
    """
    def __init__(self):
        """
        params : none
        basic empty init :)
        """

    def rink_distance(self, x,y):
        """
        :param x : x coordinates
        :type x : double
        :param y : y coordinates
        :type y : double

        :rtype : double
        :return : distance taking the coordinates x and y
        returns the distance from the rink on the stadium depending on the x and y coordinates of the hockey dataframe
        (Note, we removz 89 from the coordinate to take in account the playable surface on the stadium)
        """
        return np.sqrt((np.abs(x)-89)**2+np.abs(y)**2)
        
    def get_probabilities(self,df):
        """
        :param df : Dataframe of the Hockey
        :type  df : pandas.DataFrame

        :rtype : list of double
        :return : probability list of goal for each distance range
        returns the distance from the rink on the stadium depending on the x and y coordinates of the hockey dataframe
        (Note, we removz 89 from the coordinate to take in account the playable surface on the stadium)
        """
        proba_list = []
        count_list = []
        for i in range (0,100 ,10):
            j = i+10
            df_temp = df[(df.distance >=i) & (df.distance <j)]
            df_temp['count'] = df_temp['result.event']
            df_temp = df_temp[['result.event','count']]
            if 'Goal' in df_temp['result.event'].unique():
                df_temp= df_temp.groupby(['result.event'], as_index=False ).count()
                proba_list.append(df_temp['count'].iloc[0]/ (df_temp['count'].iloc[0] + df_temp['count'].iloc[1]))
                count_list.append(df_temp['count'].iloc[0] + df_temp['count'].iloc[1])
            else:
                proba_list.append(0)
                count_list.append(0)
        print(count_list)                
        return proba_list

        