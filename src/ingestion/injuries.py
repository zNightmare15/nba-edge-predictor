"""Injury data collection and tracking."""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import pandas as pd
from src.utils.logger import logger
from src.utils.db import get_connection

def fetch_current_injuries() -> pd.DataFrame:
    """Fetch current NBA injury report using nbainjuries or fallback."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    logger.info(f"Fetching injury report for {today_str}...")

    try:
        import nbainjuries
        # nbainjuries has scrape or get methods depending on version
        if hasattr(nbainjuries, "get_injury_report"):
            df = nbainjuries.get_injury_report()
        elif hasattr(nbainjuries, "scrape"):
            df = nbainjuries.scrape()
        else:
            df = pd.DataFrame()
    except Exception as e:
        logger.warning(f"nbainjuries package call failed: {e}. Generating placeholder/empty report.")
        df = pd.DataFrame()

    if df.empty:
        # Return empty structured dataframe
        return pd.DataFrame(columns=["report_date", "player_id", "player_name", "team_abbr", "status", "reason"])

    # Standardize columns
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    df["report_date"] = today_str
    return df

def save_injuries_to_db(df: pd.DataFrame, db_path: str = "data/nba_stats.db") -> int:
    """Store injury report rows in SQLite."""
    if df.empty:
        return 0

    conn = get_connection(db_path)
    inserted = 0
    with conn:
        for _, row in df.iterrows():
            conn.execute(
                """
                INSERT OR REPLACE INTO injury_reports (report_date, player_id, player_name, team_abbr, status, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("report_date"),
                    row.get("player_id", 0),
                    row.get("player_name", ""),
                    row.get("team_abbr", ""),
                    row.get("status", "Available"),
                    row.get("reason", ""),
                )
            )
            inserted += 1
    conn.close()
    logger.info(f"Stored {inserted} injury records in database.")
    return inserted

