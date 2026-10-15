"""Complete training orchestration pipeline for all models."""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from src.utils.logger import logger
from src.models.minutes_model import MinutesModel
from src.models.stat_model import StatModel
from src.models.evaluate import evaluate_predictions

def train_all_models(
    feature_matrix_path: str = "data/processed/features.parquet",
    model_dir: str = "data/models",
    target_stats: List[str] = ["pts", "reb", "ast", "fg3_made", "pra"],
    test_season: str = "2023-24",
    val_season: str = "2022-23",
) -> Dict[str, Any]:
    """Train the full model hierarchy: Minutes model -> Stat models."""
    path = Path(feature_matrix_path)
    if not path.exists():
        raise FileNotFoundError(f"Feature matrix not found at {path}. Run feature builder first.")

    logger.info(f"Loading feature matrix from {path}...")
    df = pd.read_parquet(path)

    # Chronological train / val / test split by season
    train_mask = (df["season"] < val_season)
    val_mask = (df["season"] == val_season)
    test_mask = (df["season"] == test_season)

    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()

    logger.info(f"Dataset split: Train={len(train_df)} rows, Val={len(val_df)} rows, Test={len(test_df)} rows")

    results = {}

    # 1. Train Minutes Model
    logger.info("=== STEP 1: TRAINING MINUTES SUB-MODEL ===")
    min_model = MinutesModel(model_dir=model_dir)
    min_metrics = min_model.train(
        X_train=train_df,
        y_train=train_df["minutes"],
        X_val=val_df,
        y_val=val_df["minutes"],
    )
    results["minutes"] = min_metrics

    # Inject predicted minutes as a feature into all datasets
    train_df["predicted_minutes"] = min_model.predict(train_df)
    val_df["predicted_minutes"] = min_model.predict(val_df)
    test_df["predicted_minutes"] = min_model.predict(test_df)

    # 2. Train Stat Models
    logger.info("=== STEP 2: TRAINING PER-STAT ENSEMBLE MODELS ===")
    for stat in target_stats:
        if stat not in train_df.columns:
            logger.warning(f"Target stat '{stat}' not found in dataset. Skipping.")
            continue

        stat_model = StatModel(stat_name=stat, model_dir=model_dir)
        stat_metrics = stat_model.train(
            X_train=train_df,
            y_train=train_df[stat],
            X_val=val_df,
            y_val=val_df[stat],
        )

        # Test evaluation
        test_preds = stat_model.predict(test_df)
        test_eval = evaluate_predictions(test_df[stat].values, test_preds, stat)
        logger.info(f"[{stat.upper()}] Test Evaluation: MAE={test_eval['mae']:.2f}, R2={test_eval['r2']:.2f}")

        results[stat] = {
            "val_metrics": stat_metrics,
            "test_metrics": test_eval,
        }

    logger.info("All models trained and saved successfully.")
    return results

if __name__ == "__main__":
    train_all_models()

