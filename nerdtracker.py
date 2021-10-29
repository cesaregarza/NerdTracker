# %%
print("Initializing nerdtracker")
import nerdtracker
import mss, time, datetime
from PIL import Image
import numpy as np
import pandas as pd
import sqlalchemy as db

db_data = {
    "username": "nerdtracker",
    "password": "iwishiknewhowtopressmouse1",
    "db_url":   "nerdtracker.cegarza.com:3306/nerd_tracker_sql_db"
}

def return_engine():
    db_url = f"{db_data['username']}:{db_data['password']}@{db_data['db_url']}"
    engine = db.create_engine(f"mysql+pymysql://{db_url}")
    return engine

engine = return_engine()

nerds = [
    "Joy#1648235",
    "ASKINNER99",
    "Unwitty#9383394",
    "Luckyclikyclika",
    "CycoChris",
    "Cali#4288543",
    "Woodster#8827717",
    "Timus#6825894",
]

# %%
print("Initialized")
player_list = None
with mss.mss() as sct:
    monitor = {
        "top": 0,
        "left": 0,
        "width": 1920,
        "height": 1080
    }
    last_lobby_time = 0
    last_screenshot_time = 0
    while True:
        frame = np.array(sct.grab(monitor))
        if time.time() - last_screenshot_time < 5:
            time.sleep(2)
            continue

        if nerdtracker.check_if_lobby_screen(frame[:160, :400].copy()):
            raw_player_reads    = nerdtracker.read_each_entry_modern_warfare(frame[238:832, 154:596].copy())
            if raw_player_reads == [[]]:
                continue

            print("Retrieving Stats")

            if (time.time() - last_lobby_time) > 10:
                if player_list is None:
                    player_list = nerdtracker.Player_List_Class(raw_player_reads, engine)
                else:
                    player_list = player_list.restart_list(raw_player_reads)
            else:
                player_list.new_snapshot(raw_player_reads)
                last_loby_time = time.time()
            
            if player_list is None:
                player_list = nerdtracker.Player_List_Class(raw_player_reads, engine)
            
            df = pd.DataFrame([[*x[:-1], x[-1][0][1], x[-1][2][1], x[-1][7][1]] if (x[-1] is not None) else [*x, None, None] for x in player_list.player_list], columns=["Name", "Controller", "KDR", "Win%", "Current Win Streak"])
            print(df.loc[~df['Name'].isin(nerdtracker.nerd_list)])
            last_lobby_time     = time.time()
            
        else:
            time.sleep(3)