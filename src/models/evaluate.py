"""Model evaluation and backtesting metrics."""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from src.utils.logger import logger

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, stat_name: str) -> Dict[str, float]:
    """Calculate key evaluation metrics for predictions."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    within_1 = np.mean(np.abs(y_true - y_pred) <= 1.0)
    within_3 = np.mean(np.abs(y_true - y_pred) <= 3.0)

    return {
        "stat": stat_name,
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "within_1_pct": float(within_1 * 100),
        "within_3_pct": float(within_3 * 100),
    }

def calculate_directional_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    lines: np.ndarray
) -> Dict[str, float]:
    """Calculate directional accuracy (Over/Under hit rate) against book lines."""
    predicted_over = y_pred > lines
    actual_over = y_true > lines

    correct = predicted_over == actual_over
    hit_rate = float(np.mean(correct))

    return {
        "hit_rate": hit_rate,
        "total_bets": int(len(y_true)),
        "correct_bets": int(np.sum(correct)),
    }

