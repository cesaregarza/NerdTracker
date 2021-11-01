from datetime import datetime, timedelta
from typing import Dict, Optional, Union
from urllib import parse
import pandas as pd
from ..constants.tracker_columns import tracker_columns
import re


TIMEDELTA_REGEX = (r'((?P<days>-?\d+)d)?'
                   r'((?P<hours>-?\d+)h)?'
                   r'((?P<minutes>-?\d+)m)?'
                   r'((?P<seconds>-?\d+\.?\d+)s)?')
TIMEDELTA_PATTERN = re.compile(TIMEDELTA_REGEX, re.IGNORECASE)

STAT_MAP = {
    "K/D Ratio":            "overall_kdr",
    "Kills":                "overall_kills",
    "Win %":                "overall_win_percentage",
    "Wins":                 "overall_wins",
    "Losses":               "overall_losses",
    "Best Killstreak":      "overall_best_killstreak",
    "Ties":                 "overall_ties",
    "Current Win Streak":   "overall_current_win_streak",
    "Avg. Life":            "overall_avg_life",
    "Assists":              "overall_assists",
    "Score/min":            "overall_score_per_minute",
    "Score":                "overall_score",
    "Score/game":           "overall_score_per_game",
}

def parse_delta(delta:str) -> timedelta:
    """Parses a timedelta string into a timedelta object

    Args:
        delta (str): String containing timedelta, e.g. "2m 05.2s"

    Returns:
        timedelta: Timedelta conversion
    """
    delta = re.sub(r'\s+', '', delta)
    match = TIMEDELTA_PATTERN.match(delta)
    if match:
        parts = {k: float(v) for k, v in match.groupdict().items() if v}
        return timedelta(**parts)

class StatsObject:
    def __init__(self, initial_stats_dict:Union[Dict[str, Optional[str]], pd.DataFrame]) -> None:

        #If the initial stats dict is a dataframe, convert it to a records dict
        if isinstance(initial_stats_dict, pd.DataFrame):
            initial_stats_dict = initial_stats_dict.to_dict(orient="records")[0]
        
        self.validate_parse_and_add(initial_stats_dict)
    
    def __get_item__(self, key:str) -> Optional[str]:
        return self.stats_dict[key]
    
    def validate_parse_and_add(self, stats_dict:Dict[str,Optional[str]]) -> None:
        self.valid = self.validate_stats(stats_dict)
        if not self.valid:
            return
        
        #Parse the stats dict into a more useful format, then remap the keys for stats from tracker.gg to match the desired column names
        stats_dict = self.parse_from_tracker(stats_dict)
        stats_dict = {STAT_MAP[key]:value for key, value in stats_dict.items() if key in STAT_MAP.keys()}

        #If the stats dict is missing any of the required columns, add them with a value of None
        for key in tracker_columns.required_columns:
            if key not in stats_dict.keys():
                stats_dict[key] = None
        
        #Remove any columns that are not required
        stats_dict = {key:value for key, value in stats_dict.items() if key in tracker_columns.required_columns}
        self.add_stats(stats_dict)
    
    def parse_from_tracker(self, tracker_dict:Dict[str,str]) -> Dict[str,Union[float, timedelta]]:

        #Clean the tracker dict, removing formatting characters. Turn most of the keys into floats, and the timedelta column into a timedelta
        clean_dict                              = self.clean_dict(tracker_dict.copy())
        new_dict                                = {key:float(value) for key, value in clean_dict.items() if key in tracker_columns.float_columns}
        new_dict[tracker_columns.avg_lifespan]  = parse_delta(clean_dict[tracker_columns.avg_lifespan])
        
        return new_dict
    
    def clean_dict(self, input_dict:Dict[str,str]) -> Dict[str, str]:
        new_dict = {}
        for key, value in input_dict.items():
            #Remove numeric formatting characters from the value
            value = re.sub("[,\%]", "", value)
            new_dict[key] = value
        
        return new_dict
    
    def update_stats(self, stats_dict:Dict[str,Optional[str]]) -> None:
        stats_dict = self.stats_dict.copy().update(stats_dict)
        self.validate_parse_and_add(stats_dict)
    
    def add_stats(self, stats_dict:Dict[str,Optional[str]]) -> None:
        for key, value in stats_dict.items():
            if key in self.stats_dict.keys():
                self.stats_dict[key] = value
    
    def validate_stats(self, stats_dict:Dict[str,Optional[str]]) -> bool:
        for key, value in stats_dict.items():
            if value is None:
                return False
        
        return True
    
    def as_pandas_series(self) -> pd.Series:
        return pd.Series(self.stats_dict)