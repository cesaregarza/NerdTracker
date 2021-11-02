from ..classes import StatsObject
from ..functions.assist import insert_costs, delete_costs, substitute_costs
from typing import List, Optional, Union, Dict
from weighted_levenshtein import lev
from cloudscraper import CloudScraper
from ..routines import retrieve_stats_from_tracker

class Node:
    def __init__(self, name:str, scraper_object:CloudScraper, position:int, similarity_threshold:float = 0.6) -> None:
        self.name                   = name
        self.position               = position
        self.similarity_threshold   = similarity_threshold
        self.scraper_object         = scraper_object
        self.stats                  = None
        self.to_delete              = False
        self.count                  = 0
        self.flag_for_stats_update  = True
    
    def __eq__(self, other:object) -> bool:
        #Check if the other object is a Node
        if isinstance(other, str):
            return self.compare_string(other)
        elif isinstance(other, Node):
            return self.compare_string(other.name)
        else:
            return False
    
    def compare_string(self, comparison_string: str) -> bool:
        """Compare the string to the node's name, and return a boolean indicating whether or not the comparison was close enough

        Args:
            comparison_string (str): The string to compare to the node's name

        Returns:
            bool: Whether or not the comparison was close enough
        """
        similarity_score = self.__get_similarity_ratio(self.name, comparison_string)
        return similarity_score >= self.similarity_threshold
    
    def __get_similarity_ratio(self, main_string:Optional[str], comparison_string:Optional[str]) -> float:
        #In case either string is None, this short circuits
        if (main_string is None) or (comparison_string is None):
            return 0
        
        #Calculate distance based on weights, then generate a similarity score by dividing by the length of the main
        #string, then subtracting it from 1. This effectively sets the maximum value at 1, for perfect match
        string_distance     = lev(main_string, comparison_string,
                                  substitute_costs  = substitute_costs,
                                  delete_costs      = delete_costs,
                                  insert_costs      = insert_costs)
        
        return (1 - string_distance / len(main_string))
    
    def _not_found(self) -> None:
        self.count     += 1
    
    def _found(self, attempted_name:str, position:int) -> None:
        self.count     = 0
        self.position = position
        if self.stats is None:
            self.flag_for_stats_update = True
    
    def update_stats(self, stats:Dict) -> None:
        """Update the node's stats with the given stats"""
        if self.stats is None:
            self.stats = StatsObject(stats)
        else:
            self.stats.update_stats(stats)
    
    def find_stats(self, attempted_name: Optional[str] = None) -> None:
        attempted_name = self.name if attempted_name is None else attempted_name
        #Check if the node has been flagged for a stats update
        if self.flag_for_stats_update:
            #If so, retrieve the stats from the tracker
            attempted_stats             = retrieve_stats_from_tracker(self.scraper_object, attempted_name)
            self.flag_for_stats_update  = False

            #Check if stats were successfully retrieved, and if so, update the node's stats and remove the flag
            if attempted_stats.valid:
                self.stats                  = attempted_stats
                self.flag_for_stats_update  = False
    
    def flag_for_deletion(self) -> None:
        """Flag the node for deletion"""
        self.to_delete = True

