from NerdTracker.nerdtracker.classes.stats_object import StatsObject
from ..functions.assist import insert_costs, delete_costs, substitute_costs
from typing import List, Optional, Union
from weighted_levenshtein import lev
from cloudscraper import CloudScraper
from ..routines import retrieve_stats_from_tracker
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from sqlalchemy.engine import Engine
import rapidfuzz
import pandas as pd

def case_when(input_string: str) -> str:
    return f"CASE WHEN pl.good_guys_team = 0 THEN {input_string} ELSE 0 END"

sql_statement = (
         "SELECT pl.unoUsername, "
                "pl.username, "
                "COUNT(*) AS times_played, "
               f"SUM({case_when('pl.kills')}) / (IFNULL(NULLIF(SUM({case_when('pl.deaths')}),0),1)) as kdr, "
                "MAX(pl.match_start) AS last_played, "
               f"SUM({case_when('pl.kills')}) / ({case_when('ma.time_played')}) AS kpm, "
               f"AVG({case_when('longest_streak')}) AS longest_streak, "
               f"SUM(ma.shots_landed) / SUM(ma.shots_fired) as accuracy "
           "FROM players pl "
     "INNER JOIN (   SELECT unoUsername, "
                           "time_played / 60 AS time_played, "
                           "longest_streak AS longest_streak, "
                           "shots_landed, "
                           "shots_fired "
                      "FROM matches " 
                  "GROUP BY unoUsername) ma "
             "ON ma.unoUsername = pl.unoUsername "
       "GROUP BY pl.unoUsername"
)

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
    
    def update_stats(self, stats:StatsObject) -> None:
        """Update the stats of the node

        Args:
            stats (StatsObject): The stats to update the node with
        """
        self.stats = stats
    
    def find_stats(self, attempted_name:str) -> None:
        """Find the stats of the node, checking if it exists in the database first and if not, retrieving them from the tracker

        Args:
            attempted_name (str): The name of the node to find stats for
        """
        #Check if the node has stats, and if not, check if it exists in the database
        if self.stats is None:
            if self.exists_in_sql(self.engine):
                self.stats                  = self.exists_in_sql(self.engine)
                self.flag_for_stats_update  = False
            else:
                #If the node doesn't exist in the database, retrieve the stats from the tracker
                attempted_stats = retrieve_stats_from_tracker(self.scraper_object, attempted_name)
                if attempted_stats.valid:
                    self.stats                  = attempted_stats
                    self.flag_for_stats_update  = False
    
    def flag_for_deletion(self) -> None:
        """Flag the node for deletion"""
        self.to_delete = True

class NodeNetwork:
    def __init__(self, scraper:CloudScraper, sql_engine:Engine, prune_threshold:int, max_nodes:int,  nodes:Optional[List[Node]] = None) -> None:
        self.scraper_object     = scraper
        self.prune_threshold    = prune_threshold
        self.max_nodes          = max_nodes
        self.nodes              = nodes
        self.engine             = sql_engine
    
    def prune(self) -> None:
        """Prune the network"""
        for node in self.nodes:
            if (node.count > self.prune_threshold) or (node.to_delete):
                self.nodes.remove(node)
        
        #If the network is too large, prune by removing nodes with the highest count
        if len(self.nodes) > self.max_nodes:
            self.nodes.sort(key=lambda x: x.count)
            self.nodes = self.nodes[:self.max_nodes]
            
    
    def add_node(self, node:Node) -> None:
        """Add a node to the network

        Args:
            node (Node): Node to be added to the network
        """
        self.nodes.append(node)
    
    def get_node(self, name:str) -> Optional[Node]:
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def get_nodes(self) -> list:
        return self.nodes
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def __getitem__(self, index:int) -> Node:
        return self.nodes[index]
    
    def is_in_network(self, string:str) -> bool:
        for node in self.nodes:
            if node == string:
                return True
        return False
    
    def parse_list(self, list_to_parse:List[str]) -> List[str]:
        """Parse the list of strings to be added to the network, and return a list of strings that are already in the network

        Args:
            list_to_parse (List[str]): List of strings to be parsed

        Returns:
            List[str]: List of strings already in the network
        """
        return [item for item in list_to_parse if self.is_in_network(item)]
    
    def new_snapshot(self, snapshot_list:List[str]) -> List[Node]:
        """Identify new nodes in the snapshot, and add them to the network, pruning the network if necessary, and updating nodes that are already in the network

        Args:
            snapshot_list (List[str]): List of strings to be added to the network

        Returns:
            List[Node]: List of nodes as per the snapshot
        """
        parsed_list = self.parse_list(snapshot_list)

        #iterate through the list, adding new nodes and updating existing ones
        for index, item in enumerate(snapshot_list):
            if self.is_in_network(item):
                self.get_node(item)._found(item, position=index)
            else:
                new_node = Node(item, self.scraper_object, position=index)
                self.add_node(new_node)

        #iterate through existing nodes, updating their count and timestamp if they are not in the parsed list
        for index, node in enumerate(self.nodes):
            if node not in parsed_list:
                node._not_found()
            
            #If there are multiple nodes with the same position, try to remove the one without stats. If none of them have stats, remove all but the one with the lowest count
            test_nodes = [test_node for test_node in self.nodes if test_node.position == node.position]
            if len(test_nodes) > 1:
                test_nodes.sort(key=lambda x: (x.stats is None, x.count))
                for test_node in test_nodes[1:]:
                    test_node.flag_for_deletion()
        
        
        #prune the network
        self.prune()

        #return the list of nodes as per the snapshot
        return self._return_snapshot(snapshot_list)
    
    def get_list_of_users_from_db(self) -> pd.Series:
        return pd.read_sql(sql_statement, self.engine)
    
    def update_stats(self) -> None:
        """Update the stats of all the flagged nodes in the network"""
        flagged_nodes = [node for node in self.nodes if node.flag_for_stats_update]
        #Use a thread pool to update the stats of all the flagged nodes
        with ThreadPoolExecutor() as executor:
            executor.map(lambda node: node.find_stats(), flagged_nodes, timeout=5)
        
    def return_node_by_position(self, position:int) -> Node:
        """Return the node at the specified position

        Args:
            position (int): Position of the node to be returned

        Returns:
            Node: Node at the specified position
        """
        #Return the node at the specified position, prioritizing the node with stats, then the one with the lowest count
        nodes_at_position = [node for node in self.nodes if node.position == position]
        nodes_at_position.sort(key=lambda x: (x.stats is None, x.count))
        return nodes_at_position[0]

    #Return nodes in the network in the order of their position in the snapshot, with priority given to nodes with stats
    def _return_snapshot(self, snapshot_list:List[str]) -> List[Node]:
        """Return the nodes in the network in the order of their position in the snapshot, with priority given to nodes with stats

        Args:
            snapshot_list (List[str]): List of strings associated with nodes in the network

        Returns:
            List[Node]: List of nodes in the network in the order of their position in the snapshot, with priority given to nodes with stats
        """
        try:
            self.update_stats()
        except TimeoutError:
            print("Timed out while updating stats")

        return_list = []
        for index, item in enumerate(snapshot_list):
            if self.is_in_network(item):
                return_list += [self.get_node(item)]
            else:
                return_list += [self.return_node_by_position(index)]

        return return_list