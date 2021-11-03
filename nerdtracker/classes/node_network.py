from typing import List, Optional, Union
from cloudscraper import CloudScraper
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from sqlalchemy.engine import Engine
from rapidfuzz import process
from .node import Node
from .stats_object import StatsObject

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

class NodeNetwork:
    def __init__(self, scraper:CloudScraper, sql_engine:Engine, prune_threshold:int, max_nodes:int,  nodes:Optional[List[Node]] = None) -> None:
        self.scraper_object     = scraper
        self.prune_threshold    = prune_threshold
        self.max_nodes          = max_nodes
        self.nodes              = nodes if nodes is not None else []
        self.engine             = sql_engine
        self.players            = self.retrieve_player_data_from_sql()
    
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
    
    def __getitem__(self, index:Union[int,str]) -> Node:
        if isinstance(index, int):
            return self.return_node_by_position(index)
        elif isinstance(index, str):
            return self.get_node(index)
        else:
            raise NotImplementedError("Index must be an int or a string")
    
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
    
    def new_snapshot(self, snapshot_list:List[str]) -> pd.DataFrame:
        """Identify new nodes in the snapshot, and add them to the network, pruning the network if necessary, and updating nodes that are already in the network

        Args:
            snapshot_list (List[str]): List of strings to be added to the network

        Returns:
            pd.DataFrame: Dataframe containing the stats for the nodes in the snapshot
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
        return_list = self._return_snapshot(snapshot_list)
        return self.return_stats_dataframe(return_list)
    
    def update_stats(self) -> None:

        #Get the stats for each flagged node
        self.update_stats_flagged()

        #Update the stats for each node if they exist in the SQL database
        for node in self.nodes:
            # try:
            #     _, _, index_found   = process.extractOne(node.name, self.players["unoUsername"], score_cutoff = 90)
            #     stats               = StatsObject(self.players.loc[index_found])
            #     node.update_stats(stats)
            #     node.name           = self.players.loc[index_found, "unoUsername"]
            _, _, index_found   = process.extractOne(node.name, self.players["unoUsername"], score_cutoff = 90)
            stats               = StatsObject(self.players.loc[index_found])
            node.update_stats(stats)
            node.name           = self.players.loc[index_found, "unoUsername"]
            # except TypeError as e:
            #     print(e)
            #     node.stats          = None

    def update_stats_flagged(self) -> None:
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
            self.update_stats_flagged()
        except TimeoutError:
            print("Timed out while updating stats")

        return_list = []
        for index, item in enumerate(snapshot_list):
            if self.is_in_network(item):
                return_list += [self.get_node(item)]
            else:
                return_list += [self.return_node_by_position(index)]

        return return_list
    
    def retrieve_player_data_from_sql(self) -> pd.DataFrame:
        """Retrieve the latest player data from the SQL Database"""
        return pd.read_sql(sql_statement, self.engine)
    
    def return_stats_dataframe(self, list_of_nodes:List[Node]) -> pd.DataFrame:
        """Return the stats of the specified nodes in a dataframe

        Args:
            list_of_nodes (List[Node]): List of nodes to be returned

        Returns:
            pd.DataFrame: Dataframe containing the stats of the specified nodes
        """
        stats_list = []
        for node in list_of_nodes:
            stats_list += [node.stats.as_pandas_series()]
        
        return pd.concat(stats_list)