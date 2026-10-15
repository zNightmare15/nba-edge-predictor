"""SQLite database management and schema definitions."""

import os
import sqlite3
from pathlib import Path
from typing import Optional
import pandas as pd
from src.utils.logger import logger

DEFAULT_DB_PATH = Path("data/nba_stats.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS player_game_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season TEXT NOT NULL,
    game_id TEXT NOT NULL,
    game_date DATE NOT NULL,
    player_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    team_id INTEGER NOT NULL,
    team_abbr TEXT NOT NULL,
    opponent_team_id INTEGER NOT NULL,
    opponent_team_abbr TEXT NOT NULL,
    is_home INTEGER NOT NULL,
    wl TEXT,
    minutes REAL,
    pts INTEGER,
    reb INTEGER,
    ast INTEGER,
    stl INTEGER,
    blk INTEGER,
    tov INTEGER,
    fg_made INTEGER,
    fg_attempted INTEGER,
    fg_pct REAL,
    fg3_made INTEGER,
    fg3_attempted INTEGER,
    fg3_pct REAL,
    ft_made INTEGER,
    ft_attempted INTEGER,
    ft_pct REAL,
    oreb INTEGER,
    dreb INTEGER,
    plus_minus REAL,
    started INTEGER DEFAULT 0,
    UNIQUE(game_id, player_id)
);

CREATE INDEX IF NOT EXISTS idx_pgl_player_date ON player_game_logs(player_id, game_date);
CREATE INDEX IF NOT EXISTS idx_pgl_game ON player_game_logs(game_id);
CREATE INDEX IF NOT EXISTS idx_pgl_season ON player_game_logs(season);
CREATE INDEX IF NOT EXISTS idx_pgl_team_date ON player_game_logs(team_abbr, game_date);

CREATE TABLE IF NOT EXISTS team_game_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season TEXT NOT NULL,
    game_id TEXT NOT NULL,
    game_date DATE NOT NULL,
    team_id INTEGER NOT NULL,
    team_abbr TEXT NOT NULL,
    opponent_team_id INTEGER NOT NULL,
    is_home INTEGER NOT NULL,
    wl TEXT,
    pts INTEGER,
    opp_pts INTEGER,
    pace REAL,
    off_rating REAL,
    def_rating REAL,
    UNIQUE(game_id, team_id)
);

CREATE INDEX IF NOT EXISTS idx_tgs_team_date ON team_game_stats(team_abbr, game_date);
CREATE INDEX IF NOT EXISTS idx_tgs_game ON team_game_stats(game_id);

CREATE TABLE IF NOT EXISTS injury_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date DATE NOT NULL,
    player_id INTEGER,
    player_name TEXT NOT NULL,
    team_abbr TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    UNIQUE(report_date, player_name, team_abbr)
);

CREATE INDEX IF NOT EXISTS idx_inj_date ON injury_reports(report_date);
CREATE INDEX IF NOT EXISTS idx_inj_player ON injury_reports(player_name);

CREATE TABLE IF NOT EXISTS game_odds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    event_id TEXT NOT NULL,
    commence_time DATETIME NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    bookmaker TEXT NOT NULL,
    market TEXT NOT NULL,
    home_spread REAL,
    away_spread REAL,
    total_over REAL,
    total_under REAL,
    home_ml_price REAL,
    away_ml_price REAL,
    fetched_at DATETIME NOT NULL,
    UNIQUE(event_id, bookmaker, market, fetched_at)
);

CREATE INDEX IF NOT EXISTS idx_odds_event ON game_odds(event_id);
CREATE INDEX IF NOT EXISTS idx_odds_time ON game_odds(commence_time);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    game_date DATE NOT NULL,
    player_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    stat_type TEXT NOT NULL,
    predicted_value REAL NOT NULL,
    actual_value REAL,
    book_line REAL,
    book_odds REAL,
    edge REAL,
    risk_level TEXT,
    bet_placed INTEGER DEFAULT 0,
    bet_result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pred_game ON predictions(game_id);
CREATE INDEX IF NOT EXISTS idx_pred_date ON predictions(game_date);
"""

def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    path = Path(db_path)
    logger.info(f"Initializing database at {path}")
    with get_connection(path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    logger.info("Database initialized successfully.")

def save_dataframe(
    df: pd.DataFrame,
    table_name: str,
    db_path: Path | str = DEFAULT_DB_PATH,
    if_exists: str = "append",
) -> int:
    """Save DataFrame to SQLite with conflict handling."""
    if df.empty:
        return 0
    with get_connection(db_path) as conn:
        # If append, we can use to_sql with if_exists="append"
        # Or execute insert or ignore if duplicates exist
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        conn.commit()
    return len(df)

