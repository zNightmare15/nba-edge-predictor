"""Orchestrates scheduled daily data refresh jobs for NBA stats, odds, and injuries."""

import time
import schedule
from datetime import datetime, timezone
from src.utils.logger import logger
from src.ingestion.injuries import fetch_current_injuries, save_injuries_to_db
from src.ingestion.odds import fetch_nba_odds, parse_and_save_odds
from src.dashboard.app import USER_SETTINGS

def daily_morning_refresh():
    """Daily morning refresh: fetch latest injury reports and odds lines."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    logger.info(f"--- Running daily morning refresh [{now}] ---")

    # 1. Update injury reports
    try:
        inj_df = fetch_current_injuries()
        save_injuries_to_db(inj_df)
    except Exception as e:
        logger.error(f"Error refreshing injuries: {e}")

    # 2. Update odds from The Odds API if key is present
    api_key = USER_SETTINGS.get("odds_api_key", "")
    if api_key and api_key != "YOUR_ODDS_API_KEY_HERE":
        try:
            odds_data = fetch_nba_odds(api_key=api_key)
            parse_and_save_odds(odds_data)
        except Exception as e:
            logger.error(f"Error refreshing odds: {e}")
    else:
        logger.info("The Odds API key not set or placeholder; skipping live odds fetch.")

def start_scheduler():
    """Start background scheduling loop."""
    logger.info("Starting NBAEdge scheduler service (scheduled for 10:00 and 18:00 UTC)...")
    schedule.every().day.at("10:00").do(daily_morning_refresh)
    schedule.every().day.at("18:00").do(daily_morning_refresh)

    # Run once immediately on start
    daily_morning_refresh()

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()

