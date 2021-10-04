import pandas as pd
import requests
import os
from tqdm import tqdm


def get_season_data(year, filepath):
    """
    Get the data from the Hockey API in JSON format for a specific season (year-year+1) and store them to a given filepath

    :param year: year of the season (example 2017 will download Season 2017-2018)
    :type year: int
    :param filepath: Path where the JSON are going to be saved
    :type filepath: str
    """
    YEAR = year
    DIRECTORY  = f"{filepath}/JSON/{YEAR}/"
    os.makedirs(DIRECTORY, exist_ok=True)
    seasons = ["01", "02", "03", "04"]
    for s in seasons:
        for g in tqdm(range(1,1300)):
            game_number = str(g).zfill(4)
            GAME_ID = f"{YEAR}{s}{game_number}"
            PATH = f"{DIRECTORY}/{GAME_ID}.json"
            if not os.path.isfile(PATH):            
                r = requests.get(f"https://statsapi.web.nhl.com/api/v1/game/{GAME_ID}/feed/live/")
                if r.status_code == 200:
                    with open(PATH, 'wb') as f:
                        f.write(r.content)  
            #else:
               # print("File already exists")