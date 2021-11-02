# from ..functions.assist import insert_costs, delete_costs, substitute_costs
# from ..routines import retrieve_stats_from_tracker
# from ..constants import nerd_list
# from ..constants.tracker_columns import tracker_columns
# from .loop_variables import Loop_Variables_Class
# from weighted_levenshtein import lev
# import cloudscraper
# import concurrent.futures
# import pandas as pd
# from rapidfuzz import fuzz, process

# class Function_Dictionary_Class:
    
#     similarity_threshold    = 0.6
#     similarity_threshold_2  = 90
#     not_found_value         = -1
#     index                   = 0
#     near_index              = 1
#     similarity_ratio        = 2
#     block                   = "block_id"
#     filler_value            = -15
#     player_name_index       = 0
#     stats_index             = 2
#     username_column         = "unoUsername"

#     def update(self, **kwargs):
#         overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
#         for key in overlapping_keys:
#             setattr(self, key, kwargs[key])

# func_dict = Function_Dictionary_Class()

# class Player_List_Class_Multi:
    
#     def __init__(self, initial_snapshot, sql_engine):
        
#         self.scraper        = cloudscraper.create_scraper()

#         def case_when(inp):
#             return f"CASE WHEN pl.good_guys_team = 0 THEN {inp} ELSE 0 END"
        
#         sql_statement = (   "SELECT pl.unoUsername, "
#                                    "pl.username, "
#                                    "COUNT(*) AS times_played, "
#                                    f"SUM({case_when('pl.kills')}) / (IFNULL(NULLIF(SUM({case_when('pl.deaths')}),0),1)) as kdr, "
#                                    "MAX(pl.match_start) AS last_played, "
#                                   f"SUM({case_when('pl.kills')}) / ({case_when('ma.time_played')}) AS kpm, "
#                                   f"AVG({case_when('longest_streak')}) AS longest_streak, "
#                                   f"SUM(ma.shots_landed) / SUM(ma.shots_fired) as accuracy "
#                               "FROM players pl "
#                         "INNER JOIN (   SELECT unoUsername, "
#                                               "time_played / 60 AS time_played, "
#                                               "longest_streak AS longest_streak, "
#                                               "shots_landed, "
#                                               "shots_fired "
#                                          "FROM matches " 
#                                      "GROUP BY unoUsername) ma "
#                                 "ON ma.unoUsername = pl.unoUsername "
#                           "GROUP BY pl.unoUsername"
#         )
#         self.users_list     = pd.read_sql(sql_statement, sql_engine)
#         self.null_row       = [None for x in self.users_list.columns]
#         self.player_list    = self._populate_player_list(self.scraper, initial_snapshot, initial=True)
    
#     def _populate_player_list(self, scraper, initial_snapshot, initial = False):

#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             result = list(executor.map(self._ignore_fraggers, initial_snapshot, timeout=5))
            
#         if initial:
#             self.all_seen_players = result
        
#         return result
    
#     def _ignore_fraggers(self, row):
#         #Ignore if players are located in the "nerd list"
#         if row[0] not in nerd_list:
#             stats = retrieve_stats_from_tracker(self.scraper, row[0])
#         else:
#             stats = {key: None for key in tracker_columns.stat_columns}
        
#         return [*row[:2], stats, *self.null_row]
    
#     def restart_list(self, initial_snapshot):
#         self.player_list    = self._populate_player_list(self.scraper, initial_snapshot)

#     def new_snapshot(self, snapshot):

#         #Generate comparisons between the existing list and the new snapshot
#         row_comparison_list = self._generate_comparisons(snapshot)
        
#         #Use list comprehension to append supplementary information As such:
#         #[New Snapshot Index, Nearest Old Snapshot Index, Shift Value] where Shift Value is simply the difference between
#         #The old index and the new index. A positive shift represents scrolling down, a negative shift represents scrolling up
#         row_comparison_list = [
#             [idx, func_dict.not_found_value, func_dict.filler_value]
#             if row[1] <= func_dict.similarity_threshold
#             else [idx, row[func_dict.index], row[func_dict.index] - idx]
#             for idx, row in enumerate(row_comparison_list)
#         ]

#         pointer_new_matched_index, pointer_main_index = [0,0]
#         pointer_new_matched_end, pointer_main_end = [False, False]
#         try:
#             scrolled = self._get_similarity_ratio(self.player_list[0][0], snapshot[0][0]) < func_dict.similarity_threshold
#         except ZeroDivisionError:
#             scrolled = False
        
#         new_list = []

#         def condition_not_found_and_first_when_scrolled(input_variables):

#             input_variables.new_list            += [main_player_row]
#             input_variables.pointer_main_index  += 1
#             return input_variables

#         def condition_not_found_and_not_first(input_variables):

#             new_stats = -1
#             input_variables.new_list += [
#                 [*input_variables.snapshot_player_row, new_stats]
#             ]
#             input_variables.pointer_new_matched_index += 1
#             return input_variables

#         def condition_found_and_already_existing(input_variables):

#             #If there's no stats associated with the player, use the new snapshot name to try and retrieve stats
#             if input_variables.main_player_row[func_dict.stats_index] is None:
#                 input_variables.new_list += [
#                     [*input_variables.snapshot_player_row, -1]
#                 ]
#             #Otherwise there's no need to update the stats since the row in question already exists
#             else:
#                 input_variables.new_list += [input_variables.main_player_row]
            
#             #Update both pointers
#             input_variables.pointer_new_matched_index   += 1
#             input_variables.pointer_main_index          += 1
#             return input_variables
        
#         def condition_index_skipped(input_variables):

#             if input_variables.scrolled and input_variables.idx == 0:
#                 input_variables.new_list += [main_player_row]
            
#             input_variables.pointer_main_index += 1
#             return input_variables

#         for idx in range(12):
#             #Re-evaluate whether or not the pointers have reached their end
#             pointer_new_matched_end = pointer_new_matched_index >= len(snapshot)
#             pointer_main_end        = pointer_main_index >= len(self.player_list)

#             #Only update the values if the end has not been reached
#             if not pointer_new_matched_end:
#                 new_player_matched_index    = row_comparison_list[pointer_new_matched_index][func_dict.near_index]
#                 snapshot_player_row         = snapshot[pointer_new_matched_index]
#             else:
#                 snapshot_player_row         = [None] * len(snapshot_player_row)
            
#             if not pointer_main_end:
#                 main_player_row             = self.player_list[pointer_main_index]
#             else:
#                 main_player_row             = [None] * len(main_player_row)
            
#             #Establish the variables dictionary on the first loop
#             if idx == 0:
#                 variables_dict = {
#                     "pointer_new_matched_index":    pointer_new_matched_index,
#                     "pointer_new_matched_end":      pointer_new_matched_end,
#                     "pointer_main_index":           pointer_main_index,
#                     "pointer_main_end":             pointer_main_end,
#                     "snapshot_player_row":          snapshot_player_row,
#                     "main_player_row":              main_player_row,
#                     "idx":                          idx,
#                     "scrolled":                     scrolled,
#                     "new_list":                     new_list,
#                 }
#                 loop_variables = Loop_Variables_Class(variables_dict)
#             #Otherwise, update some, but not all, variables in the loop variables object
#             else:
#                 variables_dict = {
#                     "pointer_new_matched_end":      pointer_new_matched_end,
#                     "pointer_main_end":             pointer_main_end,
#                     "snapshot_player_row":          snapshot_player_row,
#                     "main_player_row":              main_player_row,
#                     "idx":                          idx,
#                     "scrolled":                     scrolled,
#                 }
#                 loop_variables.update(**variables_dict)

            
#             #Condition 1: The pointed-at new player is not found
#             if new_player_matched_index < loop_variables.pointer_main_index:
#                 #Check to see if we've scrolled up and we're on the first iteration. If so, insert the first value instead
#                 #This ensures that scrolling down retains the first entry, which is the user
#                 if scrolled and idx == 0:
#                     loop_variables = condition_not_found_and_first_when_scrolled(loop_variables)
#                 else:
#                     loop_variables = condition_not_found_and_not_first(loop_variables)
#             #Condition 2: The pointed-at new player was found in the existing list
#             elif new_player_matched_index == loop_variables.pointer_main_index:
#                 loop_variables = condition_found_and_already_existing(loop_variables)
#             #Condition 3: We have skipped an index, which means we've scrolled up or we've lost players
#             else:
#                 loop_variables = condition_index_skipped(loop_variables)
            
#             pointer_main_index, pointer_new_matched_index = [loop_variables.pointer_main_index, loop_variables.pointer_new_matched_index]
        
#         #Interception in case results are too small
#         if len(loop_variables.new_list) < 2:
#             return
        
#         #Now that we have a new list, we use concurrency to retrieve the stats of multiple people at once:
#         with concurrent.futures.ThreadPoolExecutor() as executor:
#             result = list(executor.map(self._lazy_stat_retrieval, loop_variables.new_list, timeout=5))
        
#         #Now that we have a new list, we can replace the existing list with it
#         self.player_list = result

#     def _generate_comparisons(self, snapshot):
#         player_index = 0

#         #Iterate through the new snapshot
#         row_comparison = []

#         for new_snapshot_row in snapshot:
#             similarity_list = []
#             #Iterate through the currently existing player list to see what we can update from the snapshot
#             for i, player_row in enumerate(self.player_list):
#                 #If the player name is less than 4 characters, assume Tesseract messed up
#                 if len(new_snapshot_row[player_index]) < 4:
#                     similarity_list += [[i, func_dict.similarity_threshold]]
#                 elif (new_snapshot_row[player_index] is None) or (player_row[player_index] is None):
#                     similarity_list += [[i, 0]]
#                 else:
#                     #Generate a raw similarity score using a weighted Levenshtein distance that has less of a penalty for
#                     #characters that Tesseract is likely to confuse.
#                     similarity = lev(player_row[player_index], new_snapshot_row[player_index], 
#                                      substitute_costs=substitute_costs,
#                                      delete_costs=delete_costs,
#                                      insert_costs=insert_costs)

#                     #Turn the similarity score into a ratio with the original distance, then invert to generate a similarity ratio
#                     try:
#                         similarity_ratio = 1 - similarity / len(player_row[player_index])
#                     except ZeroDivisionError:
#                         similarity_ratio = 0
#                     similarity_list += [[i, similarity_ratio]]
            
#             #Add the top-scoring row to the row_comparison list
#             try:
#                 row_comparison += [sorted(similarity_list, key = lambda x: x[-1])[-1]]
#             except IndexError:
#                 continue
        
#         return row_comparison

#     def _get_similarity_ratio(self, main_string, comparison_string):
#         #Short circuit in case either the main or comparison strings are None
#         if (main_string is None) or (comparison_string is None):
#             return 0
        
#         similarity = lev(main_string, comparison_string,
#                          substitute_costs = substitute_costs,
#                          delete_costs     = delete_costs,
#                          insert_costs     = insert_costs)
        
#         return (1 - similarity / len(main_string))

#     def _likely_already_exists(self, main_string):
#         #Short circuit in case the main string is None
#         if main_string is None:
#             return False

#         #Iterate thorugh all seen players
#         for row in self.all_seen_players:
#             comparison_name = row[func_dict.player_name_index]

#             #Short circuit if the comparison name loaded is None, which shouldn't happen but might as well try
#             if comparison_name is None:
#                 continue
            
#             #Compute similarity score, then similarity ratio
#             similarity = lev(main_string, comparison_name,
#                             substitute_costs = substitute_costs,
#                             delete_costs     = delete_costs,
#                             insert_costs     = insert_costs)
            
#             try:
#                 similarity_ratio = 1 - similarity / (len(main_string))
#             except ZeroDivisionError:
#                 similarity_ratio = 0
            
#             #If the similarity ratio exceeds the threshold, return the row. Otherwise, keep iterating through the list
#             if similarity_ratio > func_dict.similarity_ratio:
#                 return row
#         #If none of the seen players hits, return False
#         return False

#     def _lazy_stat_retrieval(self, row):
#         stat        = row[func_dict.stats_index]
#         player_name = row[func_dict.player_name_index]

#         #Short circuit in case the loaded name is None
#         if player_name is None:
#             return [*row, *self.null_row] if len(row) < 11 else row
        
#         if (len(player_name) < 4):
#             return [*row, *self.null_row] if len(row) < 11 else row
        
#         truncated_name = player_name[-15:]
        
#         #Regardless if the stat has been flagged to retrieve stats, compare against the list of users to find closest match
#         try:
#             _, _, index_found = process.extractOne(truncated_name, self.users_list[func_dict.username_column], score_cutoff = func_dict.similarity_threshold_2)
#             found_row   = self.users_list.loc[index_found]
#             player_name = found_row['unoUsername']
#         except TypeError:
#             found_row   = self.null_row

#         #If the match score exceeds the similarity threshold
#         #If the stat has been flagged to retrieve stats
#         if stat == -1:
#             #Check through the list of players we've already seen
#             player_exists = self._likely_already_exists(player_name)
#             #If we haven't seen the player at all
#             if player_exists == False:
#                 #Retrieve stats from tracker.gg and add the player to our all_seen_players pool
#                 stat                    = retrieve_stats_from_tracker(self.scraper, player_name)
#                 return_row              = [*row[:-1], stat]
#                 self.all_seen_players  += [return_row]
#             #If we've seen the player and the stats are not empty, return the values previously seen
#             elif player_exists[func_dict.stats_index] is not None:
#                 return_row = player_exists
#             #If we've seen the player and he's a nerd
#             elif player_exists[func_dict.player_name_index] in nerd_list:
#                 return [*row, *self.null_row] if len(row) < 11 else row
#             #If we've seen the player and the stats are empty
#             else:
#                 #Retrieve new stats using the new player name, then add the new stats to the all_seen_players pool
#                 stat                    = retrieve_stats_from_tracker(self.scraper, player_name)
#                 return_row              = [*player_exists[:-1], stat]
#                 self.all_seen_players  += [return_row]
#         #If the stat hasn't been flagged, just return the row
#         else:
#             return [*row, *self.null_row] if len(row) < 11 else row

#         return [*return_row, *found_row]