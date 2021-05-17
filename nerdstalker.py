# %%
import nerdstalker, callofduty
import asyncio
import pandas as pd
import sqlalchemy as db

nerd_list = [
        "Joy#1648235",
        "ASKINNER99",
        "Unwitty#9383394",
        "Luckyclikyclika",
        "CycoChris",
        "Cali#4288543",
        "Woodster#8827717",
        "Timus#6825894",
        "lolgag"
]

client  = await nerdstalker.api.callofduty_client()
profile = await client.GetPlayer(callofduty.Platform.Activision, nerd_list[0])

matches = await nerdstalker.api.retrieve_matches(profile)

player_df_list = []
engagement_df_list = []
for match in matches:
    try:
        [temp_player_df, temp_engagements_df] = await nerdstalker.api.parse_given_match(match)
    except ValueError:
        continue

    player_df_list      += [temp_player_df]
    engagement_df_list  += [temp_engagements_df]


def return_engine():
    db_url = f"{db_data['username']}:{db_data['password']}@{db_data['db_url']}"
    engine = db.create_engine(f"mysql+pymysql://{db_url}")
    return engine

engine = return_engine()


# %%
player_df       = pd.concat(player_df_list)
engagement_df   = pd.concat(engagement_df_list).rename(columns={"time": "timestamp"})

matches_list = pd.read_sql("SELECT DISTINCT match_id FROM player_match_list", engine)['match_id']
player_df.loc[~player_df.index.isin(matches_list)].to_sql("player_match_list", engine, if_exists="append")

engagement_df.loc[~engagement_df['match_id'].isin(matches_list)].to_sql("engagements", engine, if_exists="append", index=False)

# %%
