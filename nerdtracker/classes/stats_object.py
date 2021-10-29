from typing import Dict, Optional
import pandas as pd


class StatsObject:
    def __init__(self, initial_stats_dict:Dict[str, Optional[str]]) -> None:
        self.stats_dict     = initial_stats_dict
        self.valid          = self.validate_stats()
        if self.valid:
            self.stats_dict = self.clean_dict()
    
    def clean_dict(self) -> Dict[str, str]:
        new_dict = {}
        for key, value in self.stats_dict.items():
            value = float(value.replace("[,s\%]"))
            new_dict[key] = value
        
        return new_dict
    
    def validate_stats(self) -> bool:
        for key, value in self.stats_dict.items():
            if value is None:
                return False
        
        return True
    
    def as_pandas_series(self) -> pd.Series:
        return pd.Series(self.stats_dict)