"""Matchup and opponent feature engineering."""

import numpy as np
import pandas as pd
from src.utils.logger import logger

def compute_matchup_features(player_logs: pd.DataFrame, team_stats: pd.DataFrame) -> pd.DataFrame:
    """Compute matchup-specific features against opposing teams."""
    logger.info("Computing matchup features...")
    df = player_logs.copy()

    # Ensure date sorting
    df = df.sort_values(["player_id", "game_date"]).reset_index(drop=True)

    # 1. Player historical performance vs specific opponent (last 5 meetings)
    if "opponent_team_abbr" in df.columns:
        opp_grouped = df.groupby(["player_id", "opponent_team_abbr"], sort=False)
        for stat in ["pts", "reb", "ast", "fg3_made", "minutes"]:
            if stat in df.columns:
                df[f"vs_opp_{stat}_avg"] = (
                    opp_grouped[stat]
                    .transform(lambda s: s.rolling(window=5, min_periods=1).mean().shift(1))
                    .fillna(df[f"{stat}_season_avg"] if f"{stat}_season_avg" in df.columns else df[stat].mean())
                )

    # 2. Team-level rolling metrics if team_stats is provided
    if not team_stats.empty and "team_abbr" in team_stats.columns:
        t_stats = team_stats.sort_values(["team_abbr", "game_date"]).reset_index(drop=True)
        t_group = t_stats.groupby("team_abbr", sort=False)

        t_stats["team_def_rating_10"] = t_group["def_rating"].transform(
            lambda s: s.rolling(window=10, min_periods=2).mean().shift(1)
        )
        t_stats["team_pace_10"] = t_group["pace"].transform(
            lambda s: s.rolling(window=10, min_periods=2).mean().shift(1)
        )

        # Merge opponent team defensive rating and pace into player logs
        opp_metrics = t_stats[["game_id", "team_abbr", "team_def_rating_10", "team_pace_10"]].rename(
            columns={
                "team_abbr": "opponent_team_abbr",
                "team_def_rating_10": "opp_def_rating_10",
                "team_pace_10": "opp_pace_10",
            }
        )
        df = df.merge(opp_metrics, on=["game_id", "opponent_team_abbr"], how="left")
    else:
        df["opp_def_rating_10"] = 110.0  # League average fallback
        df["opp_pace_10"] = 99.0

    df["opp_def_rating_10"] = df["opp_def_rating_10"].fillna(110.0)
    df["opp_pace_10"] = df["opp_pace_10"].fillna(99.0)

    logger.info("Matchup features computed.")
    return df

