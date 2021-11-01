from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib import parse
import pandas as pd
from ..constants.tracker_columns import tracker_columns
import re


TIMEDELTA_REGEX = (r'((?P<days>-?\d+)d)?'
                   r'((?P<hours>-?\d+)h)?'
                   r'((?P<minutes>-?\d+)m)?'
                   r'((?P<seconds>-?\d+\.?\d+)s)?')
TIMEDELTA_PATTERN = re.compile(TIMEDELTA_REGEX, re.IGNORECASE)

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
    def __init__(self, initial_stats_dict:Dict[str, Optional[str]]) -> None:
        self.valid = self.validate_stats(initial_stats_dict)
        if not self.valid:
            return
        
        
    
    def parse_from_tracker(self, tracker_dict:Dict[str,str]) -> Dict[str,float]:

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
    
    def validate_stats(self, stats_dict:Dict[str,Optional[str]]) -> bool:
        for key, value in stats_dict.items():
            if value is None:
                return False
        
        return True
    
    def as_pandas_series(self) -> pd.Series:
        return pd.Series(self.stats_dict)