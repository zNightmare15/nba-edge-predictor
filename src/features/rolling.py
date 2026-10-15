"""Rolling window feature computation for player performance statistics.

Computes time-series features (rolling means, EWMA, trends, etc.) for each
player's game-by-game stats.  All features are shifted by one game to prevent
data leakage: feature values for game *t* use only data from games < *t*.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ols_slope(arr: np.ndarray) -> float:
    """Return the OLS slope of *arr* regressed against [0, 1, …, n-1].

    If the array has fewer than 2 non-NaN values the result is NaN.
    """
    valid = arr[~np.isnan(arr)]
    n = len(valid)
    if n < 2:
        return np.nan
    x = np.arange(n, dtype=np.float64)
    x_mean = x.mean()
    y_mean = valid.mean()
    denom = ((x - x_mean) ** 2).sum()
    if denom == 0:
        return 0.0
    return float(((x - x_mean) * (valid - y_mean)).sum() / denom)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_rolling_features(
    df: pd.DataFrame,
    stat_cols: list[str],
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """Add rolling / expanding / EWMA features for each stat column.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain at least ``player_id``, ``game_date``, ``season``, and
        every column listed in *stat_cols*.
    stat_cols : list[str]
        Stat columns to featurise (e.g. ``["pts", "reb", "ast", "fg3_made",
        "minutes"]``).
    windows : list[int], optional
        Rolling-window sizes.  Defaults to ``[3, 5, 10, 20]``.

    Returns
    -------
    pd.DataFrame
        The original dataframe augmented with new feature columns.

    Notes
    -----
    *   Sorts by ``(player_id, game_date)`` internally.
    *   Every rolling/expanding/ewma call is followed by ``.shift(1)`` within
        each ``player_id`` group to ensure temporal integrity.
    *   NaN values produced by insufficient history are forward-filled with the
        season expanding mean where possible, then with zero.
    """
    if windows is None:
        windows = [3, 5, 10, 20]

    required = {"player_id", "game_date", "season"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {missing}")

    missing_stats = [c for c in stat_cols if c not in df.columns]
    if missing_stats:
        raise ValueError(f"Stat columns not found in DataFrame: {missing_stats}")

    logger.info(
        "Computing rolling features for %d stats × %d window sizes on %d rows",
        len(stat_cols),
        len(windows),
        len(df),
    )

    # Sort — this is critical for temporal correctness.
    df = df.sort_values(["player_id", "game_date"]).reset_index(drop=True)

    grouped = df.groupby("player_id", sort=False)

    for stat in stat_cols:
        raw = df[stat].astype(float)

        # ---- last_1: previous-game raw value --------------------------------
        df[f"{stat}_last_1"] = grouped[stat].shift(1)

        # ---- rolling means --------------------------------------------------
        for n in windows:
            df[f"{stat}_roll_{n}"] = (
                grouped[stat]
                .transform(
                    lambda s, _n=n: s.rolling(window=_n, min_periods=1).mean().shift(1)
                )
            )

        # ---- season expanding mean (season average to date) ------------------
        # Group by (player_id, season), compute expanding mean, then shift.
        season_group = df.groupby(["player_id", "season"], sort=False)
        df[f"{stat}_season_avg"] = (
            season_group[stat]
            .transform(lambda s: s.expanding(min_periods=1).mean().shift(1))
        )

        # ---- EWMA with span=10 ----------------------------------------------
        df[f"{stat}_ewma_10"] = (
            grouped[stat]
            .transform(
                lambda s: s.ewm(span=10, min_periods=1, adjust=False).mean().shift(1)
            )
        )

        # ---- rolling std with window=10 -------------------------------------
        df[f"{stat}_std_10"] = (
            grouped[stat]
            .transform(
                lambda s: s.rolling(window=10, min_periods=3).std().shift(1)
            )
        )

        # ---- trend_5: OLS slope over the last 5 games -----------------------
        df[f"{stat}_trend_5"] = (
            grouped[stat]
            .transform(
                lambda s: (
                    s.rolling(window=5, min_periods=3)
                    .apply(_ols_slope, raw=True)
                    .shift(1)
                )
            )
        )

        # ---- pct_change_5: (roll_5 − roll_20) / roll_20 --------------------
        roll5_col = f"{stat}_roll_5"
        roll20_col = f"{stat}_roll_20"
        df[f"{stat}_pct_change_5"] = np.where(
            df[roll20_col].abs() > 1e-6,
            (df[roll5_col] - df[roll20_col]) / df[roll20_col],
            0.0,
        )

    # ------------------------------------------------------------------
    # Fill NaN: use season average where available, then 0
    # ------------------------------------------------------------------
    new_feat_cols = [
        c
        for c in df.columns
        if any(
            c.endswith(sfx)
            for sfx in [
                "_last_1",
                "_season_avg",
                "_ewma_10",
                "_std_10",
                "_trend_5",
                "_pct_change_5",
            ]
        )
        or any(f"_roll_{n}" in c for n in windows)
    ]

    for col in new_feat_cols:
        # Determine the base stat for this feature column
        base_stat: Optional[str] = None
        for stat in stat_cols:
            if col.startswith(f"{stat}_"):
                base_stat = stat
                break

        if base_stat is not None:
            season_avg_col = f"{base_stat}_season_avg"
            if season_avg_col in df.columns:
                df[col] = df[col].fillna(df[season_avg_col])

        df[col] = df[col].fillna(0.0)

    logger.info(
        "Rolling features computed — %d new columns added", len(new_feat_cols)
    )
    return df
