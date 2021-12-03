import numpy as np
import collections
def angle(gp, p):
    """
        gp - goal coordinates
        p- puck coordinates
        angle in degrees
    """
    if gp[0] > 0:
        vector = (gp[0] - p[0])+((gp[1]-p[1])*1j)
        angle = np.angle(vector,deg=True)
    else:
        vector = (p[0]-gp[0])+((p[1]-gp[1])*1j)
        angle = np.angle(vector,deg=True)
    return angle

def distance(gp, p):
    """
        gp - goal coordinates
        p- puck coordinates
    """
    distance = np.sqrt((gp[0] - p[0])**2 + (gp[1] - p[1])**2)
    return distance

def penalty_time_dict(row):
    # print(f"gamePk {row['gamePk']}")
    events = row['result.event']
    if events[0]=='Penalty':
        penalty_index=0
        scoring_index=1
    else:
        penalty_index=1
        scoring_index=0

    ## Source for writing this default dict: https://stackoverflow.com/a/5029958
    penalty_addition_dict = collections.defaultdict(lambda: collections.defaultdict(int))  ## Contains time: {"awayAddition":+2,"homeAddition":-2}
        
    penalty_periodtypes = np.array(row['about.periodType'][penalty_index])
    penalty_ishome = np.array(row['isHome'][penalty_index]).astype('bool')
    scoring_ishome = np.array(row['isHome'][scoring_index]).astype('bool')
    penalty_gameseconds= np.array(row['totalGameSeconds'][penalty_index]).astype(int)
    scoring_gameseconds= np.array(row['totalGameSeconds'][scoring_index]).astype(int)
    penalty_minutes = np.array(row['result.penaltyMinutes'][penalty_index]).astype(int)

    #home
    penalty_periodtypes_home = penalty_periodtypes[penalty_ishome]
    penalty_gameseconds_home = penalty_gameseconds[penalty_ishome]
    scoring_gameseconds_home = scoring_gameseconds[scoring_ishome]
    penalty_minutes_home = penalty_minutes[penalty_ishome]

    #away
    penalty_isaway = np.logical_not(penalty_ishome)
    penalty_periodtypes_away = penalty_periodtypes[penalty_isaway]
    penalty_gameseconds_away= penalty_gameseconds[penalty_isaway]
    scoring_gameseconds_away = scoring_gameseconds[np.logical_not(scoring_ishome)]
    penalty_minutes_away = penalty_minutes[penalty_isaway]
   

    # Home Penalties
    scoring_index = 0
    for (penalty_minute,penalty_periodtype,penalty_gamesecond) in zip(penalty_minutes_home,penalty_periodtypes_home,penalty_gameseconds_home):
        penalty_seconds = int(penalty_minute*60)
        estimated_penalty_end_time= int(penalty_gamesecond+penalty_seconds)
        if penalty_periodtype!="OVERTIME":
            penalty_addition_dict[penalty_gamesecond]["homeAddition"] -= 1
        else:
            penalty_addition_dict[penalty_gamesecond]["awayAddition"] += 1
        if penalty_seconds==120.0 and penalty_periodtype!="OVERTIME":
            while scoring_index<len(scoring_gameseconds_away)-1 and scoring_gameseconds_away[scoring_index]<=penalty_gamesecond:
                scoring_index+=1
            if scoring_index<=len(scoring_gameseconds_away)-1: ## No Goals by away
                nearest_next_goalsecond = scoring_gameseconds_away[scoring_index]
            else:
                nearest_next_goalsecond=-1

            if nearest_next_goalsecond>penalty_gamesecond and nearest_next_goalsecond<=estimated_penalty_end_time:
                penalty_addition_dict[nearest_next_goalsecond]["homeAddition"]+=1
                if scoring_index<len(scoring_gameseconds_home)-1:
                    scoring_index+=1

            else:
                penalty_addition_dict[estimated_penalty_end_time]["homeAddition"]+=1
        else:
            if penalty_periodtype!="OVERTIME":
                penalty_addition_dict[estimated_penalty_end_time]["homeAddition"]+=1
            else:
                penalty_addition_dict[penalty_gamesecond]["awayAddition"] -= 1

    # Away Penalties (TODO: Form a function for both away and home, if you get time)
   
    # Away Penalties
    scoring_index = 0
    for (penalty_minute,penalty_periodtype,penalty_gamesecond) in zip(penalty_minutes_away,penalty_periodtypes_away,penalty_gameseconds_away):
        penalty_seconds = int(penalty_minute*60)
        estimated_penalty_end_time= int(penalty_gamesecond+penalty_seconds)
        if penalty_periodtype!="OVERTIME":
            penalty_addition_dict[penalty_gamesecond]["awayAddition"] -= 1
        else:

            penalty_addition_dict[penalty_gamesecond]["homeAddition"] += 1

        if penalty_seconds==120.0 and penalty_periodtype!="OVERTIME":
            while  scoring_index<len(scoring_gameseconds_home)-1 and scoring_gameseconds_home[scoring_index]<=penalty_gamesecond :
                scoring_index+=1
            if scoring_index<=len(scoring_gameseconds_home)-1:
                nearest_next_goalsecond = scoring_gameseconds_home[scoring_index]
            else:
                nearest_next_goalsecond=-1
            if nearest_next_goalsecond>penalty_gamesecond and nearest_next_goalsecond<=estimated_penalty_end_time:
                penalty_addition_dict[nearest_next_goalsecond]["awayAddition"]+=1                 
                if scoring_index<len(scoring_gameseconds_home)-1:
                    scoring_index+=1
            else:
                penalty_addition_dict[estimated_penalty_end_time]["awayAddition"]+=1
        else:
            if penalty_periodtype!="OVERTIME":
                penalty_addition_dict[estimated_penalty_end_time]["awayAddition"]+=1
            else:
                penalty_addition_dict[estimated_penalty_end_time]["homeAddition"] -= 1
    ordered_penalties = collections.OrderedDict(sorted(penalty_addition_dict.items()))

    

    return ordered_penalties


def getPenaltyTimePeriods(row):
    dc=row
    penalty_time_periods = []
    awaySum = 0
    homeSum = 0
    foundEnd=True
    for time in dc:
        if foundEnd:
            startTime =time
            foundEnd=False
        awayAddition = dc[time]['awayAddition']
        homeAddition = dc[time]['homeAddition']
        awaySum += awayAddition
        homeSum += homeAddition

        if (awaySum==0 and homeSum==0):
            foundEnd = True
            endTime = time
            penalty_time_periods.append((startTime,endTime))
    return penalty_time_periods


if __name__ == "__main__":
    a = (-89, 0)
    b = (-89, -15)
    print(angle(a, b))
    print(distance(a,b))