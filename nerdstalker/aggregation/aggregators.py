import pandas as pd

map_remap = {
    "mp_deadzone":      "Arklov Peak",
    "mp_aniyah_tac":    "Aniyah Incursion",
    "mp_hackney_am":    "Hackney Yard",
    "mp_backlot2":      "Talsik Backlot",
    "mp_runner":        "Gun Runner",
    "mp_scrapyard":     "Abandoned Scrapyard",
    "mp_cave_am":       "Azhir Cave",
    "mp_crash2":        "Crash",
    "mp_oilrig":        "Petrov Oil Rig",
    "mp_hardhat":       "Hardhat",
    "mp_garden":        "Cheshire Park",
    "mp_rust":          "Rust",
    "mp_spear":         "Rammaza",
    "mp_hideout":       "Khandor Hideout",
    "mp_petrograd":     "St. Petrograd",
    "mp_shipment":      "Shipment",
    "mp_killhouse":     "Killhouse",
    "mp_m_speed":       "Shoothouse",
    "mp_harbor":        "Suldal Harbor",
    "mp_emporium":      "Atlas Superstore",
    "mp_vacant":        "Vacant",
    "mp_village2":      "Hovec Sawmill",
    "mp_broadcast2":    "Broadcast",
    "mp_piccadilly":    "Picadilly"
}

agg_dict = {
    "Assists":              "sum",
    "Wallbangs":            "sum",
    "Headshots":            "sum",
    "Executions":           "sum",
    "Suicides":             "sum",
    "Percent Time Moving":  "mean",
    "Longest Streak":       "mean",
    "Assaults":             "sum",
    "Defenses":             "sum",
    "Capture Assists":      "sum",
    "Captures":             "sum",
    "Neutral Captures":     "sum",
}

def nerd_aggregator(sql_engine):

    #Retrieve nerd data
    sql_statement = ("SELECT * "
                       "FROM player_match_list pml "
                      "WHERE pml.unoUsername in (SELECT nt.unoUsername "
                                               "FROM nerd_table nt)")
    nerd_stats          = pd.read_sql(sql_statement, sql_engine)

    full_engagements    = pd.read_sql("SELECT * FROM engagements",  sql_engine)
    first_bloods        = pd.read_sql("SELECT * FROM first_bloods", sql_engine)
    full_matches        = pd.read_sql("SELECT * from full_matches", sql_engine)

    #Compile map data
    nerd_map_stats  = nerd_stats.groupby(["unoUsername", "map_id"]) \
                                .agg({"Kills":    "sum",
                                      "Deaths":   "sum",
                                      "match_id": "count"})

    nerd_map_stats['KDR']   = nerd_map_stats['Kills'] / nerd_map_stats['Deaths'].replace(0,1)

    #Obtain best map statistics
    best_map                = nerd_map_stats.loc[nerd_map_stats['match_id'] > 1] \
                                            .groupby(pd.Grouper(level=0)) \
                                            .agg({"KDR": ["idxmax", "max"]})
    
    best_map.columns        = ["Best Map", "Best Map KDR"]
    best_map["Best Map"]    = best_map["Best Map"].apply(lambda x: x[1]).replace(map_remap)


    #Start generating an aggregate dataframe that contains the data
    nerd_aggregate = nerd_stats.groupby("unoUsername") \
                               .agg({"Kills": "sum", "Deaths": "sum", "match_id": "count"}) \
                               .rename(columns={"match_id": "Match Count"})

    nerd_aggregate['KDR'] = nerd_aggregate['Kills'] / nerd_aggregate['Deaths']
    #Merge best map data into nerd aggregate
    nerd_aggregate = nerd_aggregate.merge(best_map, how="left", left_index=True, right_index=True)

    #Using the engagements, generate the first kill ratio statistic
    kill_ratio      = generate_kill_ratio(full_engagements)
    nerd_aggregate  = nerd_aggregate.merge(kill_ratio, how="left", left_index=True, right_index=True)

    #Generate average distance statistic
    mean_distance   = generate_average_distance(full_engagements, nerd_aggregate.index)
    nerd_aggregate  = nerd_aggregate.merge(mean_distance, how="left", left_index=True, right_index=True)

    #Generate first blood statistics
    first_blood_col         = first_bloods.value_counts("attacker").to_frame()
    first_blood_col.columns = ["First Bloods"]
    first_blood_col.index   = first_blood_col.index.rename("unoUsername")

    #Merge into nerd aggregate
    nerd_aggregate = nerd_aggregate.merge(first_blood_col, how="left", left_index=True, right_index=True)
    
    #Fill na with zeros and compute first bloods per game
    nerd_aggregate['First Bloods']          = nerd_aggregate['First Bloods'].fillna(0)
    nerd_aggregate['First Bloods per Game'] = nerd_aggregate['First Bloods'] / nerd_aggregate['Match Count']

    #Start aggregating by username
    full_match_aggregate    = full_matches.groupby("unoUsername").agg(agg_dict)
    nerd_aggregate          = nerd_aggregate.merge(full_match_aggregate, how="left", left_index=True, right_index=True)

    #Start producing new columns
    nerd_aggregate["Percent Headshots"]         = nerd_aggregate['Headshots']       / nerd_aggregate['Kills']
    nerd_aggregate["Percent Wallbangs"]         = nerd_aggregate['Wallbangs']       / nerd_aggregate['Kills']
    nerd_aggregate["Assaults per Game"]         = nerd_aggregate['Assaults']        / nerd_aggregate['Match Count']
    nerd_aggregate["Defenses per Game"]         = nerd_aggregate['Defenses']        / nerd_aggregate['Match Count']
    nerd_aggregate["Capture Assists per Game"]  = nerd_aggregate['Capture Assists'] / nerd_aggregate['Match Count']
    nerd_aggregate["Captures per Game"]         = (nerd_aggregate['Captures'] + nerd_aggregate['Neutral Captures']) / nerd_aggregate['Match Count']

    return nerd_aggregate


def generate_kill_ratio(full_engagements):
    #First, get the minimum timestamp for both attacker and victim, grouped by match id and by player
    attacker_first_kills    = full_engagements.rename(columns={"attacker": "player"}) \
                                              .groupby(["match_id", "player"])['timestamp'] \
                                              .idxmin()
    victim_first_death      = full_engagements.rename(columns={"victim": "player"}) \
                                              .groupby(["match_id", "player"])['timestamp'] \
                                              .idxmin()
    
    #Compare the two timestamps, then aggregate them using another groupby and take the mean. We use subtraction since direct comparison
    #of these two series is not allowed without renaming them. This is a much more flexible approach before taking the mean.
    #The mean forces the booleans into giving integers, with a 1 indicating that the player's first kill shows up before their
    #first death, and a 0 for the reverse on a match-player basis. Then, the second groupby with a mean will give a ratio
    #of how many first engagements each player "wins"
    comparison = (attacker_first_kills - victim_first_death) < 0
    comparison = comparison.groupby("player").mean()
    comparison = comparison.to_frame()

    #Rename the index to prepare it for return
    comparison.index = comparison.index.rename("unoUsername")
    #Rename the column as well
    comparison.columns = ["First Engagement Ratio"]
    return comparison

def generate_average_distance(full_engagements, nerd_list):

    #Filter before groupby to increase speed significantly
    full_engagements    = full_engagements.loc[full_engagements['attacker'].isin(nerd_list)]

    #Obtain the mean distance as grouped by the list of full engagements
    mean_distance           = full_engagements.groupby(["attacker"])['distance'].mean()
    mean_distance.index     = mean_distance.index.rename("unoUsername")
    mean_distance.columns   = ["Average Kill Distance"]
    return mean_distance