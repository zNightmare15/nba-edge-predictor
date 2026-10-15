"""Market features derived from sportsbook odds."""

import numpy as np
import pandas as pd
from src.utils.logger import logger

def merge_odds_features(feature_df: pd.DataFrame, odds_df: pd.DataFrame) -> pd.DataFrame:
    """Merge betting market totals and spreads as features."""
    logger.info("Merging market odds features...")
    df = feature_df.copy()

    if odds_df.empty:
        # Default league average lines when no live odds are available
        df["implied_total"] = 224.5
        df["spread"] = 0.0
        df["abs_spread"] = 0.0
        df["is_big_favorite"] = 0
        df["is_big_underdog"] = 0
        df["implied_win_prob"] = 0.50
        return df

    # Calculate average game totals and spreads across bookmakers
    game_lines = odds_df.groupby("game_id").agg({
        "total_over": "mean",
        "home_spread": "mean",
    }).reset_index().rename(columns={
        "total_over": "implied_total",
        "home_spread": "spread",
    })

    df = df.merge(game_lines, on="game_id", how="left")

    df["implied_total"] = df["implied_total"].fillna(224.5)
    df["spread"] = df["spread"].fillna(0.0)

    # Adjust spread sign if team is away
    if "is_home" in df.columns:
        df["spread"] = np.where(df["is_home"] == 1, df["spread"], -df["spread"])

    df["abs_spread"] = df["spread"].abs()
    df["is_big_favorite"] = (df["spread"] < -10.0).astype(int)
    df["is_big_underdog"] = (df["spread"] > 10.0).astype(int)

    # Implied win probability approximation from spread: Normal CDF with sigma ~ 12
    # P(win) ~ 1 - Phi(spread / 12)
    from scipy.stats import norm
    df["implied_win_prob"] = 1.0 - norm.cdf(df["spread"] / 12.0)

    logger.info("Market features merged.")
    return df

