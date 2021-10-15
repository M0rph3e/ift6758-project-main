import numpy as np
from  ift6758.data.data_acquisition import Season

from ipywidgets import widgets, interact, RadioButtons, IntSlider, Output, Layout, Dropdown
from ipywidgets.embed import embed_minimal_html

from scipy.ndimage import gaussian_filter
import plotly.graph_objects as go
import pandas as pd
import json

def get_team_time(df_clean):
    sel_columns = ['gamePk','result.event','team.name','about.period','about.periodTime','about.periodTimeRemaining']
    df1 = df_clean[sel_columns].drop_duplicates() 
    df2 = df1.sort_values('about.periodTime', ascending=False).drop_duplicates(['gamePk','about.period'])
    df2['periodTimePlayed'] = df2.apply (lambda row: time_played(row), axis=1)
    df3 = df2.groupby('gamePk')['periodTimePlayed'].sum()
    df4 = df1[['gamePk','team.name']].drop_duplicates()
    df4['gameTime'] = df4.apply(lambda x: df3.get(key = x['gamePk']),axis=1)
    df5 = df4.groupby(['team.name'])['gameTime'].sum()
    total_time = df5.sum()
    return df5.to_dict(),total_time


def advanced_visualization(year=2018,team_name="Montréal Canadiens",bin_width=1,sigma=2):
    """
    Agregates the shots at each coordinate and Returns semi rink size (85,100) of excess shots per game.
    :param year: year of the season (example 2017 Season 2017-2018)
    :type year: int
    :param team_name: team name
    :type team_name: str

    :rtype: np.array
    :return: Returns semi rink size (85,100) of excess shots per game.
    """
    def bin_coordinates(row):
        """
        takes a row and manipulates the coordinates. Return coordinates with binning of 1x1 sqft.
        :param row: row of df
        :type row: df row
        """
        if row['coordinates.x'] <0:
            ## Taking mirror image to account for hands of hockey stick
            x_bin = -row['coordinates.x']
            y_bin= 42.5-row['coordinates.y']
        else:
            x_bin = row['coordinates.x']
            y_bin= 42.5+row['coordinates.y']
        
        
        return  np.floor(x_bin), np.floor(y_bin)
    def copyToOutput(row,out):
        """
        Setting out array from df
        """
        out[int(row['y_bin']),int(row['x_bin'])]+=row['shots_average']
        return "copiedToOutput"
    def sum_bin(out,bin_width):
        """
        Sum up bin_widthxbin_width square and assign the all the cells in the square the sum value
        """
        for j in range(0,out.shape[0],bin_width):
            for i in range(0,out.shape[1],bin_width):
                bin_sum=0
                for j1 in range(bin_width):
                    for i1 in range(bin_width):
                        if j+j1<out.shape[0] and i+i1<out.shape[1]:
                            bin_sum += out[j+j1][i+i1] 
                for j1 in range(bin_width):
                    for i1 in range(bin_width):
                        if j+j1<out.shape[0] and i+i1<out.shape[1]:
                            out[j+j1][i+i1] = bin_sum                

    season = Season(year,"../ift6758/data")
    df_clean = season.clean_data()
    rink_size = (85,100)
    out = np.zeros(rink_size) #Out matrix which stores the final output

    num_teams = df_clean['team.name'].unique().shape[0]
    print(f"num_teams {num_teams} df_clean shape {df_clean.shape}")
        
    ## Reference: https://stackoverflow.com/a/52363890
    coordinates_df = df_clean.apply(lambda row: bin_coordinates(row),axis='columns', result_type='expand').rename({0: 'x_bin', 1: 'y_bin'}, axis=1)
    df_clean = pd.concat([df_clean, coordinates_df], axis='columns')
    print(f"df_clean shape after concatenating coordinates {df_clean.shape}")

    num_games_by_team = df_clean[['team.name','gamePk']].drop_duplicates().groupby('team.name')['gamePk'].count().to_dict()
    print(f"games played by teams {num_games_by_team}")
    
    df_group1 = df_clean.groupby(['team.name','x_bin','y_bin'])['result.event'].count().reset_index()
    df_group1['shots_average'] = df_group1['result.event']
    # df_group1['shots_average'] = df_group1.apply(lambda r: r['result.event'] /num_games_by_team[r['team.name']],axis=1)
    df2 = df_group1.drop('result.event',axis=1)
    # print(f"df2 {df2.shape} {df2[['team.name','x_bin','y_bin']].drop_duplicates().shape}")
    df_group2 = df2.groupby(['x_bin','y_bin'])['shots_average'].sum()
    df_group3 = df2[['team.name','x_bin','y_bin']].drop_duplicates().groupby(['x_bin','y_bin'])['team.name'].count()
    # sum_shots_coordinate_dict = df_group2.to_dict()
    # count_shots_coordinate_dict = df_group3.to_dict()
    avg_shots_coordinate_dict = (df_group2/num_teams).to_dict()
    for k,v in avg_shots_coordinate_dict.items():
        out[int(k[1]),int(k[0])]-=v
    # print(f"sum_shots_coordinate_dict {sum_shots_coordinate_dict}")
    # print(f"count_shots_coordinate_dict {count_shots_coordinate_dict}")
    # df2['excess_shots'] = df2.apply(lambda row: row['shots_average'] ,axis=1)
    # df2['excess_shots'] = df2.apply(lambda row: avg_shots_coordinate_dict[(row['x_bin'],row['y_bin'])],axis=1)
    # df2['excess_shots'] = df2.apply(lambda row: row['shots_average'] - sum_shots_coordinate_dict[(row['x_bin'],row['y_bin'])]/count_shots_coordinate_dict[(row['x_bin'],row['y_bin'])],axis=1)
    # df2['excess_shots'] = df2.apply(lambda row: row['shots_average'] - avg_shots_coordinate_dict[(row['x_bin'],row['y_bin'])],axis=1)

    df3 = df2[df2['team.name']==team_name]


    df3.apply(lambda row: copyToOutput(row,out),axis=1)
    sum_bin(out,bin_width)
    if sigma>0:
        out_gaussian = gaussian_filter(out, sigma=sigma)
    print(df3[(df3['x_bin']==66)&(df3['y_bin']==61)])
    return out_gaussian

