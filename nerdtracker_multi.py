# %%
print("Initializing")
import nerdtracker
import mss, time
import numpy as np
import pandas as pd
import concurrent.futures


# %%
player_list = None
#Screenshots
with mss.mss() as sct:
    #Establish the monitor size
    monitor = {
        "top": 0,
        "left": 0,
        "width": 1920,
        "height": 1080
    }
    print("Initialized, ready to track")

    #Set up last lobby time and last screenshot time at UNIX timestamp 0
    last_lobby_time = 0
    last_screenshot_time = 0
    while True:
        #Take a screenshot and turn it into a numpy array
        frame = np.array(sct.grab(monitor))
        #If we last took a screenshot less than 5 seconds ago, sleep before trying again
        if time.time() - last_screenshot_time < 2:
            time.sleep(2)
            continue
        
        #Check if we're at the lobby screen for the top subsection of the screen
        if nerdtracker.check_if_lobby_screen(frame[:160, :400].copy()):
            #Use OCR to read each entry, specifically for Modern Warfare
            raw_player_reads    = nerdtracker.read_each_entry_modern_warfare(frame[238:832, 154:596].copy())
            #If nothing was returned, try again
            if raw_player_reads == [[]]:
                continue
                

            print("Retrieving Stats")
            try:
                #Restart the player list if it's been more than 10 seconds since the last lobby
                if (time.time() - last_lobby_time) > 10:
                    #If player_list hasn't been initialized, initialize it
                    if player_list is None:
                        player_list = nerdtracker.Player_List_Class_Multi(raw_player_reads)
                    else:
                        player_list = player_list.restart_list(raw_player_reads)
                else:
                    #If it's the same lobby, add a new snapshot
                    player_list.new_snapshot(raw_player_reads)
                
                if player_list is None:
                    player_list = nerdtracker.Player_List_Class_Multi(raw_player_reads)
            except concurrent.futures.TimeoutError:
                print("Timeout, trying again")
                continue

            #Create a dataframe from the player list
            df = pd.DataFrame(player_list.player_list, columns=["Name", "Controller", "Dict"])

            #Manipulate the dataframe and create a display dataframe
            stats_df = nerdtracker.transform_dataframe(df['Dict'].apply(pd.Series))
            
            df              = pd.concat([df.iloc[:, :-1], stats_df], axis=1)
            display_df      = df[nerdtracker.tracker_columns.display_columns].sort_values(nerdtracker.tracker_columns.kdr, ascending=True)
            print(display_df.loc[~display_df["Name"].isin(nerdtracker.nerd_list)].drop_duplicates())

            last_lobby_time     = time.time()
            
        else:
            time.sleep(3)