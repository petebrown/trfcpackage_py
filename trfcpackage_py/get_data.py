import pandas as pd

def assign_mins_played(role, min_on, min_off, min_so):
    if role == "starter":
        if pd.isna(min_off) and pd.isna(min_so):
            return 90
        elif ~pd.isna(min_off):
            return min_off
        elif ~pd.isna(min_so):
            return min_so
    elif role == "sub":
        if pd.isna(min_off) and pd.isna(min_so):
            return 90 - min_on
        elif ~pd.isna(min_off):
            return min_off - min_on
        elif ~pd.isna(min_so):
            return min_so - min_on
        
def get_subs_and_reds():
    subs_and_reds = pd.read_csv("https://raw.githubusercontent.com/petebrown/scrape-events/main/data/subs-and-reds.csv")

    return subs_and_reds

def get_player_stats():
    player_stats = pd.read_csv("https://raw.githubusercontent.com/petebrown/update-player-stats/main/data/players_df.csv", parse_dates = ["game_date"])

    subs_and_reds = pd.read_csv("https://raw.githubusercontent.com/petebrown/scrape-events/main/data/subs-and-reds.csv")
    
    player_stats = player_stats.rename(columns = {
        "sb_game_id": "game_id",
        "sb_player_id": "player_id"})

    player_stats.game_id = player_stats.game_id.str.replace("tpg", "").astype(int)

    player_stats = player_stats[["player_id", "player_name", "game_id", "game_date", "pl_goals", "yellow_cards", "red_cards"]]

    player_stats = player_stats.merge(subs_and_reds, how = "outer", on = ["player_id", "game_id"])

    player_stats.loc[player_stats.min_on.isna(), "role"] = "starter"
    player_stats.loc[~player_stats.min_on.isna(), "role"] = "sub"

    player_stats["mins_played"] = player_stats.apply(lambda x: assign_mins_played(x.role, x.min_on, x.min_off, x.min_so), axis = 1)

    player_stats = player_stats.sort_values(["game_date", "player_id"]).reset_index(drop = True)

    return player_stats

def get_game_ids():
    player_stats = get_player_stats()

    game_ids = player_stats[["game_date", "game_id"]].drop_duplicates().sort_values(["game_date"]).reset_index(drop = True)

    return game_ids

def get_results():
    results_df = pd.read_csv("https://raw.githubusercontent.com/petebrown/update-results/main/data/results_df.csv", parse_dates = ["game_date"])

    results_mini = pd.read_csv("https://raw.githubusercontent.com/petebrown/league-position-tool/main/docs/input/results_mini.csv", parse_dates = ["game_date"])

    game_ids = get_game_ids()
    
    results_df = results_df.drop(columns = ["home_team", "away_team", "home_goals", "away_goals", "source_url", "stadium"]).merge(game_ids, how = "left", on = "game_date").merge(results_mini[["game_date", "pts"]], how = "left", on = "game_date").rename(columns = {"pts": "ssn_pts"}).sort_values(["game_date"], ascending = False).reset_index(drop = True)

    return results_df

def get_goals():
    goals = pd.read_csv("https://raw.githubusercontent.com/petebrown/scrape-goals/main/data/goals.csv")

    results_df = get_results()

    goals = goals.drop(columns = ["player_name", "goal_details"]).merge(results_df, how = "inner", on = "game_id").sort_values(["game_date", "minute"])

    return goals

def get_player_info():
    player_info = pd.read_csv("https://raw.githubusercontent.com/petebrown/scrape-player-info/main/data/player-info.csv", parse_dates = ["player_dob"])

    return player_info

def get_results_mini():
    results_mini = pd.read_csv("https://raw.githubusercontent.com/petebrown/league-position-tool/main/docs/input/results_mini.csv", parse_dates = ["game_date"])

    return results_mini