import asyncio
import callofduty
import pandas as pd

class Function_Dictionary_Class:

    allPlayers      = "allPlayers"
    result          = "result"
    team1_score     = "team1Score"
    team2_score     = "team2Score"
    ragequit        = "isPresentAtEnd"
    player          = "player"
    player_stats    = "playerStats"
    base_keys       = [
        "duration",
        "result",
        "team1Score",
        "team2Score",
        "isPresentAtEnd"
    ]
    player_keys     = [
        "uno"
    ]

    player_stat_keys = [
        "kills",
        "deaths",
        "assists",
        "timePlayed",
        "shotsFired",
        "shotsLanded",
        "shotsMissed",
        "nearmisses",
        "accuracy",
        "wallBangs",
        "headshots",
        "distanceTraveled",
        "executions",
        "suicides",
        "percentTimeMoving",
        "longestStreak",
        "objectiveMedalModeXAssaultScore",
        "objectiveMedalModeXDefendScore",
        "objectiveMedalModeDomSecureAssistScore",
        "objectiveMedalModeDomSecureScore",
        "objectiveMedalModeDomSecureNeutralScore",
    ]

    remap = {
        "kills":                "Kills",
        "deaths":               "Deaths",
        "assists":              "Assists",
        "accuracy":             "Accuracy",
        "headshots":            "Headshots",
        "executions":           "Executions",
        "suicides":             "Suicides",
        "wallBangs":            "Wallbangs",
        "distanceTraveled":     "Distance Traveled",
        "percentTimeMoving":    "Percent Time Moving",
        "longestStreak":        "Longest Streak",
        "timePlayed":           "Time Played",
        "shotsMissed":          "Shots Missed",
        "shotsFired":           "Shots Fired",
        "shotsLanded":          "Shots Hit",
        "nearmisses":           "Near Misses",
        "objectiveMedalModeXAssaultScore":          "Assaults",
        "objectiveMedalModeXDefendScore":           "Defenses",
        "objectiveMedalModeDomSecureAssistScore":   "Capture Assists",
        "objectiveMedalModeDomSecureScore":         "Captures",
        "objectiveMedalModeDomSecureNeutralScore":  "Neutral Captures",
    }



    def update(self, **kwargs):
        overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
        for key in overlapping_keys:
            setattr(self, key, kwargs[key])

func_dict = Function_Dictionary_Class()

async def parse_full_match(client, match_id):

    arguments = [
        callofduty.Platform.Activision,
        callofduty.Title.ModernWarfare,
        callofduty.Mode.Multiplayer,
        str(match_id),
        callofduty.Language.English
    ]

    full_match = await client.GetFullMatch(*arguments)
    full_match = full_match['allPlayers']

    player_list = []
    #Loop over each player
    for player in full_match:
        try:
            row          = [player[x] for x in func_dict.base_keys]
            row         += [*[player['player'][x] for x in func_dict.player_keys]]
            row         += [x['name'] for x in player['player']['loadout'][0]['primaryWeapon']['attachments']]
            row         += [*[player['playerStats'].get(x, 0) for x in func_dict.player_stat_keys]]
            player_list += [row]
        except IndexError:
            continue
    
    df = pd.DataFrame(player_list, columns=[*func_dict.base_keys, *func_dict.player_keys,*[f"Attachment {i + 1}" for i in range(5)],*func_dict.player_stat_keys])
    df['match_id'] = str(match_id)
    df['KDR'] = df['kills'] / df['deaths'].replace(0,1)
    df['Wallbang Percent']  = df['wallBangs'] / df['kills']
    df['Headshot Percent']  = df['headshots'] / df['kills']
    return df.rename(columns = func_dict.remap)
