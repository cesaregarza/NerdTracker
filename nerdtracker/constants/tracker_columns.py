class Function_Dictionary_Class:

    name            = "Name"
    controller      = "Controller"
    uno_username    = "unoUsername"
    username        = "username"
    times_played    = "times_played"
    last_played     = "last_played"
    kpm             = "kpm"
    kdr             = "K/D Ratio"
    kills           = "Kills"
    win_perc        = "Win %"
    wins            = "Wins"
    best_killstreak = "Best Killstreak"
    losses          = "Losses"
    ties            = "Ties"
    curr_winstreak  = "Current Win Streak"
    deaths          = "Deaths"
    avg_lifespan    = "Avg. Life"
    assists         = "Assists"
    score_per_min   = "Score/min"
    score_per_game  = "Score/game"
    total_score     = "Score"
    stat_columns    = [
                        kdr,
                        kills,
                        win_perc,
                        wins,
                        best_killstreak,
                        losses,
                        ties,
                        curr_winstreak,
                        deaths,
                        avg_lifespan,
                        assists,
                        score_per_min,
                        score_per_game,
                        total_score
                    ]
    float_columns    = [
                        kdr,
                        kills,
                        win_perc,
                        wins,
                        best_killstreak,
                        losses,
                        ties,
                        curr_winstreak,
                        deaths,
                        assists,
                        score_per_min,
                        score_per_game,
                        total_score
                    ]
    display_columns = [
                        name,
                        controller,
                        uno_username,
                        username,
                        times_played,
                        "kdr",
                        last_played,
                        kpm,
                        kdr,
                        win_perc,
                        curr_winstreak
    ]
    required_columns = [
                        times_played,
                        "kdr",
                        last_played,
                        kpm,
                        'overall_kdr',
                        'overall_kills',
                        'overall_win_percentage',
                        'overall_wins',
                        'overall_losses',
                        'overall_best_killstreak',
                        'overall_ties',
                        'overall_current_win_streak',
                        'overall_avg_life',
                        'overall_assists',
                        'overall_score_per_minute',
                        'overall_score',
                        'overall_score_per_game'
    ]

tracker_columns = Function_Dictionary_Class()