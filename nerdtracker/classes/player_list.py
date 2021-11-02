# from ..functions.assist import insert_costs, delete_costs, substitute_costs
# from ..routines import retrieve_stats_from_tracker
# from ..constants import nerd_list
# from weighted_levenshtein import lev
# import cloudscraper

# class Function_Dictionary_Class:
    
#     similarity_threshold    = 0.8
#     not_found_value         = -1
#     index                   = "index"
#     near_index              = "near_index"
#     similarity_ratio        = "similarity_ratio"
#     block                   = "block_id"
#     column_names            = [
#         "near_index",
#         "similarity_ratio"
#     ]
#     filler_value            = -15

#     def update(self, **kwargs):
#         overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
#         for key in overlapping_keys:
#             setattr(self, key, kwargs[key])

# func_dict = Function_Dictionary_Class()

# class Player_List_Class:
    
#     def __init__(self, initial_snapshot):
        
#         self.scraper        = cloudscraper.create_scraper()
#         self.player_list    = [
#             [*row[:2], retrieve_stats_from_tracker(self.scraper, row[0])]
#             if row[0] not in nerd_list
#             else
#             [*row[:2], None]
#             for row in initial_snapshot
#         ]
    
#     def restart_list(self, initial_snapshot):
#         self.player_list    = [
#             [*row[:2], retrieve_stats_from_tracker(self.scraper, row[0])]
#             if row[0] not in nerd_list
#             else
#             [*row[:2], None]
#             for row in initial_snapshot
#         ]

#     def new_snapshot(self, snapshot):
        
#         #Generate comparisons between the existing list and the new snapshot
#         row_comparison_list = self._generate_comparisons(snapshot)
        
#         #Use list comprehension to append supplementary information As such:
#         #[New Snapshot Index, Nearest Old Snapshot Index, Shift Value] where Shift Value is simply the difference between
#         #The old index and the new index. A positive shift represents scrolling down, a negative shift represents scrolling up
#         row_comparison_list = [
#             [idx, func_dict.not_found_value, func_dict.filler_value]
#             if row[1] <= func_dict.similarity_threshold
#             else [idx, row[0], row[0] - idx]
#             for idx, row in enumerate(row_comparison_list)
#         ]

#         #Find the indices of the new values not found in the existing list
#         new_player_indices  = [
#             row[0]
#             for row in row_comparison_list 
#             if row[-1] == func_dict.filler_value
#             ]

#         num_new_players     = len(new_player_indices)
        
#         #Generate a list of indices of the players that were matched with an entry on the master list
#         existing_indices = [
#             row[1]
#             for row in row_comparison_list
#             if row[-1] != func_dict.filler_value
#         ]

#         #Indices should be from 0 to n, no exceptions. This will create a list from 0 to n, then compare with the indices
#         #we have in our new snapshot that already exist. The result will be a list of missing indices that are not in the
#         #snapshot, but are in the master list
#         try:
#             missing_indices = list(set(range(max(existing_indices))).difference(set(existing_indices)))
#         except ValueError:
#             return
        
#         #Calculate how many players were removed
#         num_players_removed = len(missing_indices)
#         assumed_player_scrolls = row_comparison_list[0][1]
#         delta_players = num_new_players - num_players_removed + abs(assumed_player_scrolls)

#         pointer_new_matched_index, pointer_main_index = [0,0]
#         new_list = []

#         for _ in range(delta_players + len(self.player_list)):
#             #Cap both pointers to prevent index errors
#             pointer_main_index          = min(pointer_main_index, len(self.player_list) - 1)
#             pointer_new_matched_index   = min(pointer_new_matched_index, len(snapshot) - 1)

#             #Use the pointers to retrieve the appropriate variables and rows for future comparison
#             new_player_matched_index    = row_comparison_list[pointer_new_matched_index][1]
#             main_player_row             = self.player_list[pointer_main_index]
#             snapshot_player_row         = snapshot[pointer_new_matched_index]

#             #Condition 1: The pointed-at new player is not found
#             if new_player_matched_index < pointer_main_index:
#                 #Check to see if we've likely scrolled up
#                 if (assumed_player_scrolls < 0) and new_player_matched_index > 0:
#                     new_list += [
#                         main_player_row
#                     ]
#                     assumed_player_scrolls += 1
#                 else:
#                     #Retrieve stats and add it to the new_list variable, increment pointer by 1
#                     if snapshot_player_row[0] not in nerd_list:
#                         new_stats = retrieve_stats_from_tracker(self.scraper, snapshot_player_row[0])
#                     else:
#                         new_stats = None
#                     new_list += [
#                         [
#                             *snapshot_player_row[:2],
#                             new_stats
#                         ]
#                     ]
#                 pointer_new_matched_index += 1
#                 continue
#             #Condition 2: The pointed-at new player already exists
#             elif new_player_matched_index == pointer_main_index:
#                 #If there's no stats associated with the player, use the new snapshot name to try and retrieve stats
#                 if main_player_row[-1] is None:
#                     if snapshot_player_row[0] not in nerd_list:
#                         new_stats = retrieve_stats_from_tracker(self.scraper, snapshot_player_row[0])
#                     else:
#                         new_stats = None
#                     new_list += [
#                         [
#                             *snapshot_player_row[:2], new_stats
#                         ]
#                     ]
#                 #Otherwise, there's no need to update the stats since the row name is correct
#                 else:
#                     new_list += [
#                         main_player_row
#                     ]
#                 #Then update both pointers
#                 pointer_new_matched_index += 1
#                 pointer_main_index += 1
#                 continue
#             #Third condition: We have skipped an index, which either means scrolling up or removed players
#             else:
#                 #if the assumed player scrolls is greater than 0, kick it into the player list
#                 if assumed_player_scrolls > 0:
#                     new_list += [
#                         main_player_row
#                     ]
#                     assumed_player_scrolls -= 1

#                 #Just need to update the main index pointer and continue
#                 pointer_main_index += 1
#                 continue
        
#         #Now that we have a new list, we can replace the existing list with it
#         self.player_list = new_list


#     def _generate_comparisons(self, snapshot):
#         player_index = 0

#         #Iterate through the new snapshot
#         row_comparison = []

#         for new_snapshot_row in snapshot:
#             similarity_list = []
#             #Iterate through the currently existing player list to see what we can update from the snapshot
#             for i, player_row in enumerate(self.player_list):
#                 #Generate a raw similarity score using a weighted Levenshtein distance that has less of a penalty for
#                 #characters that Tesseract is likely to confuse.
#                 similarity = lev(player_row[player_index], new_snapshot_row[player_index], \
#                                  substitute_costs=substitute_costs,
#                                  delete_costs=delete_costs,
#                                  insert_costs=insert_costs)
                
#                 #Turn the similarity score into a ratio with the original distance, then invert to generate a similarity ratio
#                 similarity_ratio = 1 - similarity / len(player_row[player_index])
#                 similarity_list += [[i, similarity_ratio]]
            
#             #Add the top-scoring row to the row_comparison list
#             row_comparison += [sorted(similarity_list, key = lambda x: x[-1])[-1]]
        
#         return row_comparison