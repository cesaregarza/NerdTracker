from ..functions.assist import insert_costs, delete_costs, substitute_costs
from ..routines import retrieve_stats_from_tracker
from ..constants import nerd_list
from weighted_levenshtein import lev
import cloudscraper
import concurrent.futures
import pandas as pd

class Function_Dictionary_Class:
    
    similarity_threshold    = 0.6
    not_found_value         = -1
    index                   = 0
    near_index              = 1
    similarity_ratio        = 2
    block                   = "block_id"
    filler_value            = -15
    player_name_index       = 0
    stats_index             = 2

    def update(self, **kwargs):
        overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
        for key in overlapping_keys:
            setattr(self, key, kwargs[key])

func_dict = Function_Dictionary_Class()

class Player_List_Class_Multi:
    
    def __init__(self, initial_snapshot):
        
        self.scraper        = cloudscraper.create_scraper()
        self.player_list    = self._populate_player_list(self.scraper, initial_snapshot)
    
    def _populate_player_list(self, scraper, initial_snapshot):

        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = list(executor.map(self._ignore_fraggers, initial_snapshot))
        
        return result
    
    def _ignore_fraggers(self, row):
        if row[0] not in nerd_list:
            stats = retrieve_stats_from_tracker(self.scraper, row[0])
        else:
            stats = None
        
        return [*row[:2], stats]
    
    def restart_list(self, initial_snapshot):
        self.player_list    = self._populate_player_list(self.scraper, initial_snapshot)

    def new_snapshot_(self, snapshot):

        #Generate comparisons between the existing list and the new snapshot
        row_comparison_list = self._generate_comparisons(snapshot)
        
        #Use list comprehension to append supplementary information As such:
        #[New Snapshot Index, Nearest Old Snapshot Index, Shift Value] where Shift Value is simply the difference between
        #The old index and the new index. A positive shift represents scrolling down, a negative shift represents scrolling up
        row_comparison_list = [
            [idx, func_dict.not_found_value, func_dict.filler_value]
            if row[1] <= func_dict.similarity_threshold
            else [idx, row[func_dict.index], row[func_dict.index] - idx]
            for idx, row in enumerate(row_comparison_list)
        ]

        pointer_new_matched_index, pointer_main_index = [0,0]
        pointer_new_matched_end, pointer_main_end = [False, False]

        scrolled = self._get_similarity_ratio(self.player_list[0][0], snapshot[0][0]) < func_dict.similarity_threshold
        new_list = []

        for idx in range(12):
            #Re-evaluate whether or not the pointers have reached their end
            pointer_new_matched_end = pointer_new_matched_index >= len(snapshot)
            pointer_main_end        = pointer_main_index >= len(self.player_list)

            #Only update the values if the end has not been reached
            if not pointer_new_matched_end:
                new_player_matched_index    = row_comparison_list[pointer_new_matched_index][func_dict.near_index]
                snapshot_player_row         = snapshot[pointer_new_matched_index]
            
            if not pointer_main_end:
                main_player_row             = self.player_list[pointer_main_index]
            
            #Condition 1: The pointed-at new player is not found
            if new_player_matched_index < pointer_main_index:
                #Check to see if we've scrolled up and we're on the first iteration. If so, insert the first value instead
                #This ensures that scrolling down retains the first entry, which is the user
                if scrolled and idx == 0:
                    new_list += [
                        main_player_row
                    ]
                    continue
                else:
                    #If the above condition is not met, we check if the new player is part of the list of nerds. Otherwise,
                    #flag for lazy retrieval of stats later
                    if snapshot_player_row[func_dict.player_name_index] not in nerd_list:
                        new_stats = -1
                    else:
                        new_stats = None
                    
                    new_list += [
                        [*snapshot_player_row[:func_dict.stats_index], new_stats]
                    ]
                pointer_new_matched_index += 1
                continue
            #Condition 2: The pointed-at new player was found in the existing list
            elif new_player_matched_index == pointer_main_index:
                #If there's no stats associated with the player, use the new snapshot name to try and retrieve stats
                if main_player_row[func_dict.stats_index] is None:
                    #Check if the player is in the list of nerds to flag for lazy retrieval of stats later
                    if snapshot_player_row[func_dict.player_name_index] not in nerd_list:
                        new_stats = -1
                    else:
                        new_stats = None
                    
                    new_list += [
                        [*snapshot_player_row[:func_dict.stats_index], new_stats]
                    ]
                #Otherwise, there's no needs to update the stats since the row in question already exists
                else:
                    new_list += [main_player_row]
                
                #Then update both pointers
                pointer_new_matched_index += 1
                pointer_main_index        += 1
                continue
            #Condition 3: We have skipped an index, which means we've scrolled up or we've lost players
            else:
                if not scrolled:
                    new_list += [main_player_row]

                pointer_main_index += 1
                continue
        
        #Interception in case results are too small
        if len(self.player_list) < 2:
            return
        
        #Now that we have a new list, we use concurrency to retrieve the stats of multiple people at once:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = list(executor.map(self._lazy_stat_retrieval, new_list))
        #Now that we have a new list, we can replace the existing list with it
        self.player_list = result
    

    def new_snapshot(self, snapshot):
        
        #Generate comparisons between the existing list and the new snapshot
        row_comparison_list = self._generate_comparisons(snapshot)
        
        #Use list comprehension to append supplementary information As such:
        #[New Snapshot Index, Nearest Old Snapshot Index, Shift Value] where Shift Value is simply the difference between
        #The old index and the new index. A positive shift represents scrolling down, a negative shift represents scrolling up
        row_comparison_list = [
            [idx, func_dict.not_found_value, func_dict.filler_value]
            if row[1] <= func_dict.similarity_threshold
            else [idx, row[func_dict.index], row[func_dict.index] - idx]
            for idx, row in enumerate(row_comparison_list)
        ]

        #Find the indices of the new values not found in the existing list
        new_player_indices  = [
            row[0]
            for row in row_comparison_list 
            if row[-1] == func_dict.filler_value
            ]

        num_new_players     = len(new_player_indices)
        
        #Generate a list of indices of the players that were matched with an entry on the master list
        existing_indices = [
            row[1]
            for row in row_comparison_list
            if row[-1] != func_dict.filler_value
        ]

        #Indices should be from 0 to n, no exceptions. This will create a list from 0 to n, then compare with the indices
        #we have in our new snapshot that already exist. The result will be a list of missing indices that are not in the
        #snapshot, but are in the master list
        try:
            missing_indices = list(set(range(len(self.player_list))).difference(set(existing_indices)))
        except ValueError:
            return
        
        #Calculate how many players were removed
        num_players_removed = len(missing_indices)
        assumed_scroll_state = row_comparison_list[0][1]
        
        delta_players = num_new_players - num_players_removed + abs(assumed_scroll_state)

        pointer_new_matched_index, pointer_main_index = [0,0]
        new_list = []

        print(f"assumed_scroll_state: {assumed_scroll_state}")
        print(f"delta: {delta_players}; list length: {delta_players + len(self.player_list)}")
        print(pd.DataFrame(snapshot))
        print(pd.DataFrame(row_comparison_list))

        for idx in range(delta_players + len(self.player_list)):
            #Cap both pointers to prevent index errors
            pointer_main_index          = min(pointer_main_index, len(self.player_list) - 1)
            pointer_new_matched_index   = min(pointer_new_matched_index, len(snapshot) - 1)

            #Use the pointers to retrieve the appropriate variables and rows for future comparison
            new_player_matched_index    = row_comparison_list[pointer_new_matched_index][1]
            main_player_row             = self.player_list[pointer_main_index]
            snapshot_player_row         = snapshot[pointer_new_matched_index]

            #Condition 1: The pointed-at new player is not found
            if new_player_matched_index < pointer_main_index:
                #Check to see if we've likely scrolled up
                if (assumed_scroll_state < 0) and new_player_matched_index > 0:
                    new_list += [
                        main_player_row
                    ]
                    assumed_scroll_state += 1
                    print("Condition 1a")
                else:
                    #Retrieve stats and add it to the new_list variable, increment pointer by 1
                    if snapshot_player_row[0] not in nerd_list:
                        new_stats = -1
                    else:
                        new_stats = None
                    print("Condition 1b")
                    new_list += [
                        [
                            *snapshot_player_row[:2],
                            new_stats
                        ]
                    ]
                pointer_new_matched_index += 1
                continue
            #Condition 2: The pointed-at new player already exists
            elif new_player_matched_index == pointer_main_index:
                #If there's no stats associated with the player, use the new snapshot name to try and retrieve stats
                if main_player_row[-1] is None:
                    print("Condition 2a")
                    if snapshot_player_row[0] not in nerd_list:
                        new_stats = -1
                    else:
                        new_stats = None
                    new_list += [
                        [
                            *snapshot_player_row[:2], new_stats
                        ]
                    ]
                #Otherwise, there's no need to update the stats since the row name is correct
                else:
                    print("Condition 2b")
                    new_list += [
                        main_player_row
                    ]
                #Then update both pointers
                pointer_new_matched_index += 1
                pointer_main_index += 1
                continue
            #Third condition: We have skipped an index, which either means scrolling up or removed players
            else:
                #if the assumed player scrolls is greater than 0, kick it into the player list
                if assumed_scroll_state > 0:
                    new_list += [
                        main_player_row
                    ]
                    assumed_scroll_state -= 1
                    print("Condition 3a")
                else:
                    print("Condition 3b")

                #Just need to update the main index pointer and continue
                pointer_main_index += 1
                continue
        
        #Now that we have a new list, we use concurrency to retrieve the stats of multiple people at once:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = list(executor.map(self._lazy_stat_retrieval, new_list))
        
        #Now that we have a new list, we can replace the existing list with it
        self.player_list = result


    def _generate_comparisons(self, snapshot):
        player_index = 0

        #Iterate through the new snapshot
        row_comparison = []

        for new_snapshot_row in snapshot:
            similarity_list = []
            #Iterate through the currently existing player list to see what we can update from the snapshot
            for i, player_row in enumerate(self.player_list):
                #If the player name is less than 4 characters, assume Tesseract messed up
                if len(new_snapshot_row[player_index]) < 4:
                    similarity = len(new_snapshot_row[player_index])
                else:
                    #Generate a raw similarity score using a weighted Levenshtein distance that has less of a penalty for
                    #characters that Tesseract is likely to confuse.
                    similarity = lev(player_row[player_index], new_snapshot_row[player_index], 
                                     substitute_costs=substitute_costs,
                                     delete_costs=delete_costs,
                                     insert_costs=insert_costs)
                
                #Turn the similarity score into a ratio with the original distance, then invert to generate a similarity ratio
                similarity_ratio = 1 - similarity / len(player_row[player_index])
                similarity_list += [[i, similarity_ratio]]
            
            #Add the top-scoring row to the row_comparison list
            row_comparison += [sorted(similarity_list, key = lambda x: x[-1])[-1]]
        
        return row_comparison
    
    def _get_similarity_ratio(self, main_string, comparison_string):
        similarity = lev(main_string, comparison_string,
                         substitute_costs = substitute_costs,
                         delete_costs     = delete_costs,
                         insert_costs     = insert_costs)
        
        return (1 - similarity / len(main_string))
    
    def _lazy_stat_retrieval(self, row):
        stat = row[-1]
        if stat == -1:
            stat = retrieve_stats_from_tracker(self.scraper, row[0])
        
        return [*row[:-1], stat]