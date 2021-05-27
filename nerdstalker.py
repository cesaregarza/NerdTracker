# %%
import nerdstalker, callofduty
import asyncio
import pandas as pd
import sqlalchemy as db

def return_engine():
    db_url = f"{db_data['username']}:{db_data['password']}@{db_data['db_url']}"
    engine = db.create_engine(f"mysql+pymysql://{db_url}")
    return engine

engine = return_engine()

# %%

nerd_list = [
        "Joy#1648235",
        "ASKINNER99",
        "Unwitty#9383394",
        "Luckyclikyclika",
        "CycoChris",
        "Cali#4288543",
        "Woodster#8827717",
        "Timus#6825894",
        "lolgag",
        "DrDwayyo#8559361",
        "Hotel Moscow#9934165",
]

client  = await nerdstalker.api.callofduty_client()
profile = await client.GetPlayer(callofduty.Platform.Activision, nerd_list[1])

matches = await nerdstalker.api.retrieve_matches(profile)

player_df_list = []
engagement_df_list = []
match_df_list = []
for match in matches:
    try:
        [temp_player_df, temp_engagements_df, temp_match_df] = await nerdstalker.api.parse_given_match(match, client)
    except ValueError:
        continue

    player_df_list      += [temp_player_df]
    engagement_df_list  += [temp_engagements_df]
    match_df_list       += [temp_match_df]


# %%
player_df       = pd.concat(player_df_list)
engagement_df   = pd.concat(engagement_df_list).rename(columns={"time": "timestamp"})
match_df        = pd.concat(match_df_list)

matches_list            = pd.read_sql("SELECT DISTINCT match_id FROM player_match_list", engine)['match_id']
nerd_list               = pd.read_sql("SELECT unoUsername FROM nerd_table", engine).iloc[:, 0]
player_df['is_nerd']    = player_df['unoUsername'].isin(nerd_list)
nerd_team               = player_df.groupby([
                                             pd.Grouper(level=0),
                                             pd.Grouper(key="team")
                                            ])['is_nerd'].sum() > 1

player_df = player_df.reset_index().set_index(["match_id", "team"]).drop(columns=["is_nerd"])
player_df = player_df.merge(nerd_team, how="left", left_index=True, right_index=True)
player_df = player_df.rename(columns={"is_nerd": "good_guys_team"}).reset_index().set_index("match_id")


engagement_df   = engagement_df.merge(
    player_df.reset_index()[["index", "match_id", "unoUsername"]].rename(columns = {
                                                                      "index":          "a",
                                                                      "unoUsername":    "attacker"
                                                                      }),
    how="left", on=["match_id", "a"]).merge(
    player_df.reset_index()[["index", "match_id", "unoUsername"]].rename(columns={
                                                                    "index":        "v",
                                                                    "unoUsername":  "victim"}),
    how="left", on=["match_id", "v"])

match_df = match_df.merge(
    player_df.reset_index()[["unoId", "unoUsername"]].drop_duplicates(),
    how="left", left_on="uno", right_on="unoId"
).drop(columns=["uno"])


# %%
player_df.loc[~player_df.index.isin(matches_list)].to_sql("player_match_list", engine, if_exists="append")
engagement_df.loc[~engagement_df['match_id'].isin(matches_list)].to_sql("engagements", engine, if_exists="append", index=False)
match_df.loc[~match_df['match_id'].isin(matches_list)].to_sql("full_matches", engine, index=False, if_exists="append")
# %%
first_bloods = engagement_df.sort_values(["match_id", "timestamp"]).groupby("match_id").first()
first_bloods.loc[~first_bloods.index.isin(matches_list), ["timestamp", "attacker", "victim", "cause"]].to_sql("first_bloods", engine, if_exists="append")
# %%
aggregate_df = nerdstalker.aggregation.nerd_aggregator(engine)


# %%
