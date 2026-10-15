"""Contextual features: schedule density, rest days, back-to-back, altitude."""

import numpy as np
import pandas as pd
from src.utils.logger import logger
from src.utils.constants import HIGH_ALTITUDE_TEAMS

def compute_context_features(player_logs: pd.DataFrame) -> pd.DataFrame:
    """Compute rest, travel, schedule density, and altitude context features."""
    logger.info("Computing context features...")
    df = player_logs.copy()

    df["game_date_dt"] = pd.to_datetime(df["game_date"])
    df = df.sort_values(["player_id", "game_date_dt"]).reset_index(drop=True)

    # 1. Rest days (difference in days since player's team previous game)
    player_team_group = df.groupby(["player_id", "season"], sort=False)

    df["prev_game_date"] = player_team_group["game_date_dt"].shift(1)
    df["rest_days"] = (df["game_date_dt"] - df["prev_game_date"]).dt.days - 1
    # First game of season or missing defaults to 3 days rest
    df["rest_days"] = df["rest_days"].clip(lower=0, upper=10).fillna(3)

    # 2. Back-to-back game indicator (0 days of rest between games)
    df["is_b2b"] = (df["rest_days"] == 0).astype(int)

    # 3. Schedule density: number of games in last 7 days
    # Count games in rolling 7 day window per player
    def calc_games_last_7d(sub_df):
        dates = sub_df["game_date_dt"].values
        counts = np.zeros(len(dates), dtype=int)
        for i in range(len(dates)):
            # Look backwards up to 7 days excluding current game
            window_start = dates[i] - np.timedelta64(7, "D")
            prev_dates = dates[:i]
            counts[i] = np.sum((prev_dates >= window_start) & (prev_dates < dates[i]))
        return pd.Series(counts, index=sub_df.index)

    df["games_last_7d"] = player_team_group.apply(calc_games_last_7d).reset_index(level=[0, 1], drop=True)
    df["games_last_7d"] = df["games_last_7d"].fillna(1).astype(int)

    # 4. Altitude effect (Denver / Utah games)
    df["is_altitude"] = df["opponent_team_abbr"].isin(HIGH_ALTITUDE_TEAMS).astype(int)

    # Drop temporary datetime columns
    df = df.drop(columns=["game_date_dt", "prev_game_date"], errors="ignore")

    logger.info("Context features computed.")
    return df

