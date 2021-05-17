import asyncio
import pandas as pd

async def parse_given_match(match_object):

    #Retrieve the full match details based on the Match object
    current_match = await match_object.details()

    #Skip if the mode isn't hardcore domination
    if current_match['mode'] != "dom_hc":
        raise ValueError

    #parse the resulting dict to create a dataframe that's both for players and engagements
    players_df                              = parse_match_players(current_match)
    kills_ser, deaths_ser, engagements_df   = parse_engagements(current_match)

    #Rename the series
    kills_ser.name  = "Kills"
    deaths_ser.name = "Deaths"

    #Append Kills and Deaths
    players_df = players_df.merge(
        kills_ser.to_frame(),
        how="left",
        left_on="index",
        right_index=True
    )
    players_df = players_df.merge(
        deaths_ser.to_frame(),
        how="left",
        left_on="index",
        right_index=True
    )

    #Fill na values and turn to integers, then compute KDR while avoiding division by zero
    players_df.loc[:, ["Kills", "Deaths"]] = players_df.loc[:, ["Kills", "Deaths"]].fillna(0).astype(int)
    players_df['KDR'] = players_df['Kills'] / players_df['Deaths'].replace(0,1)

    return [players_df, engagements_df]


def parse_match_players(match_dict):

    match_id        = match_dict['matchId']
    teams           = match_dict['teams']
    map_id          = match_dict['map']['mapId']
    
    #Concatenate both teams, with keys indicating their respective team
    players_df      = pd.concat(
        [
            pd.DataFrame(x)
            for x in teams
        ],
        keys=[0,1]
    )

    #Add the match ID to the dataframe, then recalculate the player index based on the team to match the engagement index
    players_df['match_id']  = match_id
    players_df['map_id']    = map_id
    players_df              = players_df.reset_index()
    players_df              = players_df.rename(columns={
        "level_0": "team",
        "level_1": "index"
    }).set_index("match_id")
    players_df['index']     = players_df['index'] + (players_df['team'] * 1000)
    return players_df

def parse_engagements(match_dict):

    match_id = match_dict['matchId']

    #Turn the engagements list of dicts into a dataframe
    engagements_df  = pd.DataFrame(match_dict['engagements'])
    
    engagements_df['match_id'] = match_id

    #Pull out all teamkills
    teamkills_index = (
        ((engagements_df['a'] <  1000) & (engagements_df['v'] <  1000)) |
        ((engagements_df['a'] >= 1000) & (engagements_df['v'] >= 1000))
    )
    #Create series for aggregate stats
    kills_series    = fix_index(engagements_df.loc[~teamkills_index].value_counts("a"))
    deaths_series   = fix_index(engagements_df.loc[~teamkills_index].value_counts("v"))

    #Compute L2 distance
    engagements_df['distance'] = (
        (engagements_df['ax'] - engagements_df['vx']) ** 2 +
        (engagements_df['ay'] - engagements_df['vy']) ** 2
    ) ** 0.5
    
    return [kills_series, deaths_series, engagements_df]

def fix_index(input_series):
    input_series.index = input_series.index.get_level_values(0)
    return input_series