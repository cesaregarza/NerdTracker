from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
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
    def __init__(self, initial_stats_dict:Union[Dict[str, Optional[str]], pd.DataFrame, pd.Series, 'StatsObject'], tracker:bool=False) -> None:
        
        #If the input is a StatsObject, just copy the stats dict
        if isinstance(initial_stats_dict, StatsObject):
            self.stats_dict = initial_stats_dict.stats_dict
            self.valid = initial_stats_dict.valid
            return
        else:
            self.stats_dict = {}
        #If the initial stats dict is a dataframe, convert it to a records dict
        if isinstance(initial_stats_dict, (pd.DataFrame, pd.Series)):
            if isinstance(initial_stats_dict, pd.Series):
                initial_stats_dict = initial_stats_dict.to_dict()
            else:
                initial_stats_dict = initial_stats_dict.to_records(orient="records")[0]
            
            tracker = False
        else:
            tracker = True
        
        self.validate_parse_and_add(initial_stats_dict, tracker=tracker)
    
    def __get_item__(self, key:str) -> Optional[str]:
        return self.stats_dict[key]
    
    def __repr__(self) -> str:
        return f"<StatsObject:\n valid:{self.valid}\n{self.stats_dict}>"
        
    def validate_parse_and_add(self, stats_dict:Dict[str,Optional[str]], tracker:bool = False) -> None:
        try:
            self.valid = self.validate_stats(stats_dict)
        except AttributeError:
            self.valid = False

        if not self.valid:
            return
        
        if tracker:
            #Parse the stats dict into a more useful format, then remap the keys for stats from tracker.gg to match the desired column names
            stats_dict = self.parse_from_tracker(stats_dict)
            stats_dict = {STAT_MAP[key]:value for key, value in stats_dict.items() if key in STAT_MAP.keys()}

        stats_dict = self.append_required_columns(stats_dict)
        stats_dict = self.remove_excess_columns(stats_dict)
        self.add_stats(stats_dict)
    
    def append_required_columns(self, stats_dict:Dict[str,Any]) -> Dict[str, Any]:
        for key in tracker_columns.required_columns:
            if key not in stats_dict.keys():
                stats_dict[key] = None
        
        return stats_dict
    
    def remove_excess_columns(self, stats_dict:Dict[str,Any]) -> Dict[str, Any]:
        return {key:value for key, value in stats_dict.items() if key in tracker_columns.required_columns}
    
    def parse_from_tracker(self, tracker_dict:Dict[str,str]) -> Dict[str,Union[float, timedelta]]:
        """Parse the tracker dict into a more useful format

        Args:
            tracker_dict (Dict[str,str]): Input dict to parse from tracker.gg

        Returns:
            Dict[str,Union[float, timedelta]]: Parsed dict
        """

        #Clean the tracker dict, removing formatting characters. Turn most of the keys into floats, and the timedelta column into a timedelta
        clean_dict                              = self.clean_dict(tracker_dict.copy())
        new_dict                                = {key:float(value) for key, value in clean_dict.items() if key in tracker_columns.float_columns}
        new_dict[tracker_columns.avg_lifespan]  = parse_delta(clean_dict[tracker_columns.avg_lifespan])
        
        return new_dict
    
    def clean_dict(self, input_dict:Dict[str,str]) -> Dict[str, str]:
        """Clean up the tracker dict by removing formatting characters and converting keys to lowercase

        Args:
            input_dict (Dict[str,str]): Input dict to clean

        Returns:
            Dict[str, str]: Cleaned dict, all strings
        """
        new_dict = {}
        for key, value in input_dict.items():
            if not isinstance(value, str):
                continue
            #Remove numeric formatting characters from the value
            value = re.sub("[,\%]", "", value)
            new_dict[key] = value
        
        return new_dict
    
    def update_stats(self, stats_dict:Dict[str,Optional[str]]) -> None:
        """Update the stats dict with the new stats

        Args:
            stats_dict (Dict[str,Optional[str]]): Stats dict to update from
        """
        if isinstance(stats_dict, StatsObject):
            stats_dict = stats_dict.stats_dict
        
        #Remove None values from the stats dict
        stats_dict = {key:value for key, value in stats_dict.items() if value is not None}
        self.stats_dict.update(stats_dict)
        self.valid = self.validate_stats(self.stats_dict)
    
    def add_stats(self, stats_dict:Dict[str,Optional[str]]) -> None:
        """Add the stats dict to the current stats dict

        Args:
            stats_dict (Dict[str,Optional[str]]): Stats dict to add
        """
        for key, value in stats_dict.items():
            if key in tracker_columns.required_columns:
                self.stats_dict[key] = value
    
    def validate_stats(self, stats_dict:Dict[str,Optional[str]]) -> bool:
        """Validate the stats dict

        Args:
            stats_dict (Dict[str,Optional[str]]): Stats dict to validate

        Returns:
            bool: Whether the stats dict is valid
        """
        for key, value in stats_dict.items():
            if value is None:
                return False
        
        return True
    
    def as_pandas_series(self) -> pd.Series:
        return pd.Series(self.stats_dict)