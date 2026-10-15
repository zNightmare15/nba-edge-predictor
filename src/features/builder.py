"""Feature matrix builder orchestrating all feature pipelines."""

from pathlib import Path
from typing import List, Optional
import pandas as pd
from src.utils.logger import logger
from src.utils.db import get_connection
from src.features.rolling import compute_rolling_features
from src.features.matchup import compute_matchup_features
from src.features.context import compute_context_features
from src.features.market import merge_odds_features

def build_feature_matrix(
    seasons: Optional[List[str]] = None,
    db_path: str = "data/nba_stats.db",
    output_path: str = "data/processed/features.parquet",
) -> pd.DataFrame:
    """Load data from database, apply all feature pipelines, and produce modeling dataset."""
    logger.info("Starting complete feature matrix construction...")
    conn = get_connection(db_path)

    query = "SELECT * FROM player_game_logs"
    if seasons:
        season_filter = "', '".join(seasons)
        query += f" WHERE season IN ('{season_filter}')"
    query += " ORDER BY player_id, game_date ASC"

    player_df = pd.read_sql_query(query, conn)

    if player_df.empty:
        logger.warning("No player game logs found in database.")
        conn.close()
        return pd.DataFrame()

    team_df = pd.read_sql_query("SELECT * FROM team_game_stats", conn)
    odds_df = pd.read_sql_query("SELECT * FROM game_odds", conn)
    conn.close()

    # 1. Target variables: pts, reb, ast, fg3_made, pra, minutes
    player_df["pra"] = player_df["pts"] + player_df["reb"] + player_df["ast"]

    stat_cols = ["pts", "reb", "ast", "fg3_made", "pra", "minutes"]

    # 2. Rolling temporal features
    df = compute_rolling_features(player_df, stat_cols=stat_cols, windows=[3, 5, 10, 20])

    # 3. Matchup features
    df = compute_matchup_features(df, team_df)

    # 4. Context features (rest, b2b, density)
    df = compute_context_features(df)

    # 5. Market features
    df = merge_odds_features(df, odds_df)

    # Save processed dataset
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    logger.info(f"Feature matrix saved successfully to {out} ({len(df)} rows, {len(df.columns)} columns).")

    return df

