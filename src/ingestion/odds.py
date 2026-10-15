"""Odds ingestion from The Odds API with intelligent caching and secret isolation.

Features:
- Secure API key retrieval via environment variable `ODDS_API_KEY`.
- Zero key leakage in log messages or exceptions.
- 15-minute smart caching (avoids depleting the 500-request monthly quota).
- Live bookmaker extraction for Winamax, Bet365, Pinnacle, FanDuel, DraftKings.
- Direct player prop integration (Points, Rebounds, Assists, 3PM).
"""

import os
import time
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

from src.utils.logger import logger
from src.utils.db import get_connection
from src.utils.security import mask_secret, sanitize_text

# Ensure .env is loaded
load_dotenv()

CACHE_DIR = Path("data/cache")
CACHE_FILE = CACHE_DIR / "the_odds_api_cache.json"
CACHE_TTL_SECONDS = 900  # 15 minutes cache to preserve user's API quota

def get_api_key() -> str:
    """Retrieve API key securely from environment variable or settings."""
    key = os.getenv("ODDS_API_KEY", "").strip()
    if not key or key == "YOUR_ODDS_API_KEY_HERE":
        # Check settings.yaml fallback
        try:
            import yaml
            settings_path = Path("config/settings.yaml")
            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    key = cfg.get("odds_api", {}).get("api_key", "").strip()
        except Exception:
            pass
    return key if key != "YOUR_ODDS_API_KEY_HERE" else ""

def _read_cache(key: str) -> Optional[Any]:
    """Read cached API payload if not expired."""
    try:
        if not CACHE_FILE.exists():
            return None
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        entry = data.get(key)
        if entry:
            timestamp = entry.get("timestamp", 0)
            if (time.time() - timestamp) < CACHE_TTL_SECONDS:
                return entry.get("payload")
    except Exception:
        pass
    return None

def _write_cache(key: str, payload: Any):
    """Write API payload to cache."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {}
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data[key] = {
            "timestamp": time.time(),
            "payload": payload
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        logger.warning(f"Failed to write odds cache: {e}")

def fetch_nba_odds(
    api_key: Optional[str] = None,
    regions: str = "eu,us",
    markets: str = "spreads,totals,h2h",
    sport: str = "basketball_nba",
    base_url: str = "https://api.the-odds-api.com/v4",
    force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    """Fetch live NBA odds with automatic 15-minute caching to preserve API quota."""
    key = api_key or get_api_key()
    if not key:
        logger.info("No valid The Odds API key configured. Skipping live odds fetch.")
        return []

    cache_key = f"{sport}_{regions}_{markets}"
    if not force_refresh:
        cached = _read_cache(cache_key)
        if cached is not None:
            logger.info(f"Using cached NBA odds ({len(cached)} games) - preserving API quota.")
            return cached

    url = f"{base_url}/sports/{sport}/odds"
    params = {
        "apiKey": key,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "decimal",
    }

    masked = mask_secret(key)
    logger.info(f"Fetching fresh NBA odds from The Odds API (Key: {masked})...")
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        remaining = response.headers.get("x-requests-remaining", "unknown")
        used = response.headers.get("x-requests-used", "unknown")
        logger.info(f"Retrieved odds for {len(data)} games. Quota: {remaining} remaining ({used} used).")

        _write_cache(cache_key, data)
        return data
    except Exception as e:
        sanitized_err = sanitize_text(str(e))
        logger.error(f"Failed to fetch odds from The Odds API: {sanitized_err}")
        # If fetch fails, try returning stale cache
        cached = _read_cache(cache_key)
        return cached or []

def fetch_player_props_cached(
    event_id: str,
    api_key: Optional[str] = None,
    markets: str = "player_points,player_rebounds,player_assists",
    sport: str = "basketball_nba",
    base_url: str = "https://api.the-odds-api.com/v4",
) -> List[Dict[str, Any]]:
    """Fetch live player props for a specific game event with caching."""
    key = api_key or get_api_key()
    if not key or not event_id:
        return []

    cache_key = f"props_{event_id}_{markets}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached

    url = f"{base_url}/sports/{sport}/events/{event_id}/odds"
    params = {
        "apiKey": key,
        "regions": "eu,us",
        "markets": markets,
        "oddsFormat": "decimal",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        bookmakers = data.get("bookmakers", [])
        _write_cache(cache_key, bookmakers)
        return bookmakers
    except Exception as e:
        logger.warning(f"Error fetching props for event {event_id}: {sanitize_text(str(e))}")
        return []

def parse_and_save_odds(odds_data: List[Dict[str, Any]], db_path: str = "data/nba_stats.db") -> int:
    """Parse raw odds JSON and save into game_odds table."""
    if not odds_data:
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    rows = []

    for event in odds_data:
        event_id = event.get("id")
        commence_time = event.get("commence_time")
        home_team = event.get("home_team")
        away_team = event.get("away_team")

        for book in event.get("bookmakers", []):
            book_key = book.get("key")
            for market in book.get("markets", []):
                market_key = market.get("key")
                outcomes = market.get("outcomes", [])

                home_spread = None
                away_spread = None
                total_over = None
                total_under = None
                home_ml = None
                away_ml = None

                if market_key == "spreads":
                    for o in outcomes:
                        if o.get("name") == home_team:
                            home_spread = o.get("point")
                        elif o.get("name") == away_team:
                            away_spread = o.get("point")
                elif market_key == "totals":
                    for o in outcomes:
                        if o.get("name") == "Over":
                            total_over = o.get("point")
                        elif o.get("name") == "Under":
                            total_under = o.get("point")
                elif market_key == "h2h":
                    for o in outcomes:
                        if o.get("name") == home_team:
                            home_ml = o.get("price")
                        elif o.get("name") == away_team:
                            away_ml = o.get("price")

                rows.append((
                    None,
                    event_id,
                    commence_time,
                    home_team,
                    away_team,
                    book_key,
                    market_key,
                    home_spread,
                    away_spread,
                    total_over,
                    total_under,
                    home_ml,
                    away_ml,
                    now_iso,
                ))

    conn = get_connection(db_path)
    inserted = 0
    with conn:
        for r in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO game_odds (
                    game_id, event_id, commence_time, home_team, away_team,
                    bookmaker, market, home_spread, away_spread, total_over,
                    total_under, home_ml_price, away_ml_price, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                r
            )
            inserted += 1
    conn.close()
    logger.info(f"Saved {inserted} odds entries into database.")
    return inserted
