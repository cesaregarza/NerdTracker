# %%
print("Initializing")
import nerdtracker
import mss, time
import numpy as np
import pandas as pd
import concurrent.futures
import datetime as dt
import colorama as cl

cl.init()
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 250)

# %%
player_list = None
db_engine = nerdtracker.return_engine()

class Function_Dictionary_Class:

    lobby_height = 160
    lobby_width  = 450
    
    player_frame_top    = 238
    player_frame_bottom = 832
    player_frame_left   = 154
    player_frame_right  = 596

    def update(self, **kwargs):
        overlapping_keys = set(kwargs.keys()).intersection(set(self.__dir__()))
        for key in overlapping_keys:
            setattr(self, key, kwargs[key])

func_dict = Function_Dictionary_Class()

#Screenshots
with mss.mss() as sct:
    #Establish the monitor size
    monitor = {
        "top": 0,
        "left": 0,
        "width": 2560,
        "height": 1440
    }
    multiplier = monitor["height"] / 1080
    print(f"{cl.Fore.GREEN}Initialized, ready to track{cl.Style.RESET_ALL}")

    #Set up last lobby time and last screenshot time at UNIX timestamp 0
    last_lobby_time = 0
    last_screenshot_time = 0
    while True:
        #Take a screenshot and turn it into a numpy array
        frame = np.array(sct.grab(monitor))
        #If we last took a screenshot less than k seconds ago, sleep before trying again
        if time.time() - last_screenshot_time < 0.5:
            time.sleep(0.5)
            continue
        else:
            last_screenshot_time = time.time()

        #Remove the alpha channel, which is always 255
        cut_frame = frame[:, :, :-1]
        
        #Check if we're at the lobby screen for the top subsection of the screen
        if nerdtracker.check_if_lobby_screen(frame[:160, :450].copy()):
            #Use OCR to read each entry, specifically for Modern Warfare
            player_frame        = frame[
                func_dict.player_frame_top : func_dict.player_frame_bottom,
                func_dict.player_frame_left : func_dict.player_frame_right
            ].copy()
            raw_player_reads    = nerdtracker.read_each_entry_modern_warfare(player_frame, multiplier)
            #If nothing was returned, try again
            if raw_player_reads == [[]]:
                continue
                

            print("Retrieving Stats")
            try:
                #Restart the player list if it's been more than 10 seconds since the last lobby
                if (time.time() - last_lobby_time) > 10:
                    #If player_list hasn't been initialized, initialize it
                    if player_list is None:
                        player_list = nerdtracker.Player_List_Class_Multi(raw_player_reads, db_engine)
                    else:
                        player_list = player_list.restart_list(raw_player_reads)
                else:
                    #If it's the same lobby, add a new snapshot
                    player_list.new_snapshot(raw_player_reads)
                
                if player_list is None:
                    player_list = nerdtracker.Player_List_Class_Multi(raw_player_reads, db_engine)
            except concurrent.futures.TimeoutError:
                print("Timeout, trying again")
                continue
            
            #Create a dataframe from the player list
            df = pd.DataFrame(player_list.player_list, columns=["Name", "Controller", "Dict", *player_list.users_list.columns])

            #Manipulate the dataframe and create a display dataframe
            stats_df = nerdtracker.transform_dataframe(df['Dict'].apply(pd.Series))
            
            df              = pd.concat([df.iloc[:, :-1], stats_df], axis=1)
            display_df      = df[nerdtracker.tracker_columns.display_columns].sort_values(nerdtracker.tracker_columns.kdr, ascending=True)
            display_df      = nerdtracker.highlight_dataframe(display_df, player_list.users_list)
            display_df      = nerdtracker.display_dataframe(display_df)
            print(display_df.loc[~display_df["Name"].isin(nerdtracker.nerd_list)].drop_duplicates())

            last_lobby_time     = time.time()
        
        #If the screen has faded to black
        elif np.mean(cut_frame) < 10 and (time.time() - last_lobby_time) < 5:
            # nerdtracker.submit_dataframe(db_engine, df)
            time.sleep(5)
            
        else:
            time.sleep(.5)