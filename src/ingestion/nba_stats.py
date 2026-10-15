"""Data ingestion for NBA statistics using nba_api."""

import time
from typing import List, Optional
import pandas as pd
from src.utils.logger import logger
from src.utils.constants import SEASONS, NBA_TEAMS
from src.utils.db import get_connection, save_dataframe

def fetch_season_player_logs(season: str, delay_seconds: float = 1.0) -> pd.DataFrame:
    """Fetch player game logs for an entire season using PlayerGameLogs."""
    from nba_api.stats.endpoints import playergamelogs

    logger.info(f"Fetching player game logs for season {season}...")
    try:
        logs = playergamelogs.PlayerGameLogs(
            season_nullable=season,
            season_type_nullable="Regular Season",
        )
        df = logs.get_data_frames()[0]
        time.sleep(delay_seconds)
    except Exception as e:
        logger.error(f"Failed to fetch player game logs for season {season}: {e}")
        return pd.DataFrame()

    if df.empty:
        return df

    # Standardize column names to lowercase
    df.columns = [col.lower() for col in df.columns]

    # Map columns to match SQLite schema
    column_mapping = {
        "game_id": "game_id",
        "game_date": "game_date",
        "player_id": "player_id",
        "player_name": "player_name",
        "team_id": "team_id",
        "team_abbreviation": "team_abbr",
        "min": "minutes",
        "pts": "pts",
        "reb": "reb",
        "ast": "ast",
        "stl": "stl",
        "blk": "blk",
        "tov": "tov",
        "fgm": "fg_made",
        "fga": "fg_attempted",
        "fg_pct": "fg_pct",
        "fg3m": "fg3_made",
        "fg3a": "fg3_attempted",
        "fg3_pct": "fg3_pct",
        "ftm": "ft_made",
        "fta": "ft_attempted",
        "ft_pct": "ft_pct",
        "oreb": "oreb",
        "dreb": "dreb",
        "plus_minus": "plus_minus",
        "wl": "wl",
    }

    processed = pd.DataFrame()
    for source_col, target_col in column_mapping.items():
        if source_col in df.columns:
            processed[target_col] = df[source_col]

    processed["season"] = season

    # Derive is_home and opponent info from MATCHUP column (e.g. 'BOS vs. NYK' or 'BOS @ MIA')
    if "matchup" in df.columns:
        processed["is_home"] = df["matchup"].apply(lambda m: 1 if "vs." in str(m) else 0)
        processed["opponent_team_abbr"] = df["matchup"].apply(
            lambda m: str(m).split(" ")[-1] if " " in str(m) else ""
        )
        # Map opponent team id
        abbr_to_id = {abbr: data["id"] for abbr, data in NBA_TEAMS.items()}
        processed["opponent_team_id"] = processed["opponent_team_abbr"].map(abbr_to_id).fillna(0).astype(int)
    else:
        processed["is_home"] = 0
        processed["opponent_team_abbr"] = ""
        processed["opponent_team_id"] = 0

    # Clean game_date to YYYY-MM-DD
    if "game_date" in processed.columns:
        processed["game_date"] = pd.to_datetime(processed["game_date"]).dt.strftime("%Y-%m-%d")

    # Handle minutes (sometimes format 'MM:SS' or float)
    if "minutes" in processed.columns:
        def parse_minutes(val):
            if pd.isna(val):
                return 0.0
            if isinstance(val, (int, float)):
                return float(val)
            val_str = str(val).strip()
            if ":" in val_str:
                parts = val_str.split(":")
                try:
                    return float(parts[0]) + float(parts[1]) / 60.0
                except (ValueError, IndexError):
                    return 0.0
            try:
                return float(val_str)
            except ValueError:
                return 0.0
        processed["minutes"] = processed["minutes"].apply(parse_minutes)

    # Started indicator (approximate by top minutes or starting flag)
    processed["started"] = 0

    return processed

def fetch_season_team_stats(season: str, delay_seconds: float = 1.0) -> pd.DataFrame:
    """Fetch team game stats for an entire season using LeagueGameLog."""
    from nba_api.stats.endpoints import leaguegamelog

    logger.info(f"Fetching team game logs for season {season}...")
    try:
        logs = leaguegamelog.LeagueGameLog(
            season=season,
            season_type_all_star="Regular Season",
            player_or_team_abbreviation="T",
        )
        df = logs.get_data_frames()[0]
        time.sleep(delay_seconds)
    except Exception as e:
        logger.error(f"Failed to fetch team logs for season {season}: {e}")
        return pd.DataFrame()

    if df.empty:
        return df

    df.columns = [c.lower() for c in df.columns]

    processed = pd.DataFrame()
    processed["season"] = season
    processed["game_id"] = df["game_id"]
    processed["game_date"] = pd.to_datetime(df["game_date"]).dt.strftime("%Y-%m-%d")
    processed["team_id"] = df["team_id"]
    processed["team_abbr"] = df["team_abbreviation"]
    processed["is_home"] = df["matchup"].apply(lambda m: 1 if "vs." in str(m) else 0)
    processed["wl"] = df["wl"]
    processed["pts"] = df["pts"]

    abbr_to_id = {abbr: data["id"] for abbr, data in NBA_TEAMS.items()}
    processed["opponent_team_abbr"] = df["matchup"].apply(lambda m: str(m).split(" ")[-1])
    processed["opponent_team_id"] = processed["opponent_team_abbr"].map(abbr_to_id).fillna(0).astype(int)

    # Merge opponent points by self-joining on game_id
    opp_pts_map = df.set_index(["game_id", "team_abbreviation"])["pts"].to_dict()
    processed["opp_pts"] = processed.apply(
        lambda row: opp_pts_map.get((row["game_id"], row["opponent_team_abbr"]), 0),
        axis=1
    )

    # Estimate pace and ratings
    # Pace ~ FGA + 0.44 * FTA - OREB + TOV
    fga = df.get("fga", 85)
    fta = df.get("fta", 22)
    oreb = df.get("oreb", 10)
    tov = df.get("tov", 14)
    est_possessions = fga + 0.44 * fta - oreb + tov
    processed["pace"] = est_possessions
    processed["off_rating"] = (processed["pts"] / processed["pace"].replace(0, 100)) * 100
    processed["def_rating"] = (processed["opp_pts"] / processed["pace"].replace(0, 100)) * 100

    return processed

def ingest_historical_seasons(seasons: Optional[List[str]] = None, db_path: str = "data/nba_stats.db") -> None:
    """Ingest multiple seasons into SQLite database."""
    if seasons is None:
        seasons = SEASONS

    conn = get_connection(db_path)

    for season in seasons:
        logger.info(f"--- Ingesting Season {season} ---")
        player_df = fetch_season_player_logs(season)
        if not player_df.empty:
            # Insert or replace into player_game_logs
            with conn:
                for _, row in player_df.iterrows():
                    cols = list(row.index)
                    placeholders = ",".join(["?"] * len(cols))
                    col_names = ",".join(cols)
                    sql = f"INSERT OR REPLACE INTO player_game_logs ({col_names}) VALUES ({placeholders})"
                    conn.execute(sql, tuple(row.values))
            logger.info(f"Saved {len(player_df)} player game logs for {season}")

        team_df = fetch_season_team_stats(season)
        if not team_df.empty:
            with conn:
                for _, row in team_df.iterrows():
                    cols = list(row.index)
                    placeholders = ",".join(["?"] * len(cols))
                    col_names = ",".join(cols)
                    sql = f"INSERT OR REPLACE INTO team_game_stats ({col_names}) VALUES ({placeholders})"
                    conn.execute(sql, tuple(row.values))
            logger.info(f"Saved {len(team_df)} team game stats for {season}")

    conn.close()
    logger.info("Historical data ingestion completed.")

