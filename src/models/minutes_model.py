"""Minutes played prediction sub-model.

Predicts expected playing time for players, factoring in rotation,
rest, blowout risk, and recent performance.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd
from src.utils.logger import logger

class MinutesModel:
    """Predicts playing time (minutes) using LightGBM Regressor."""

    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.model_dir / "minutes_lgbm.joblib"
        self.model = None
        self.feature_names = None

    def _get_feature_columns(self, df: pd.DataFrame) -> list[str]:
        """Select feature columns relevant to playing time."""
        exclude = {
            "id", "season", "game_id", "game_date", "player_id", "player_name",
            "team_id", "team_abbr", "opponent_team_id", "opponent_team_abbr",
            "wl", "pts", "reb", "ast", "stl", "blk", "tov", "pra", "minutes",
            "fg_made", "fg_attempted", "fg3_made", "fg3_attempted", "ft_made", "ft_attempted",
            "oreb", "dreb", "plus_minus"
        }
        return [c for c in df.columns if c not in exclude and np.issubdtype(df[c].dtype, np.number)]

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict[str, float]:
        """Train the LightGBM minutes model."""
        import lightgbm as lgb
        from sklearn.metrics import mean_absolute_error, root_mean_squared_error

        self.feature_names = self._get_feature_columns(X_train)
        X_tr = X_train[self.feature_names]

        logger.info(f"Training MinutesModel with {len(self.feature_names)} features on {len(X_tr)} samples (Robust Huber Loss)...")

        self.model = lgb.LGBMRegressor(
            objective="huber",
            alpha=0.9,
            num_leaves=31,
            max_depth=6,
            learning_rate=0.04,
            n_estimators=600,
            min_child_samples=20,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
        )

        eval_set = [(X_val[self.feature_names], y_val)] if X_val is not None and y_val is not None else None
        callbacks = [lgb.early_stopping(stopping_rounds=50, verbose=False)] if eval_set else None

        self.model.fit(
            X_tr,
            y_train,
            eval_set=eval_set,
            callbacks=callbacks,
        )

        train_preds = self.predict(X_train)
        train_mae = mean_absolute_error(y_train, train_preds)
        metrics = {"train_mae": float(train_mae)}

        if X_val is not None and y_val is not None:
            val_preds = self.predict(X_val)
            metrics["val_mae"] = float(mean_absolute_error(y_val, val_preds))
            metrics["val_rmse"] = float(root_mean_squared_error(y_val, val_preds))
            logger.info(f"MinutesModel Validation MAE: {metrics['val_mae']:.2f} min, RMSE: {metrics['val_rmse']:.2f} min")

        self.save()
        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict minutes played for given features."""
        if self.model is None:
            self.load()
        X_feats = X[self.feature_names] if self.feature_names else X
        preds = self.model.predict(X_feats)
        return np.clip(preds, 0.0, 48.0)

    def save(self) -> None:
        """Save model and feature names to disk."""
        data = {"model": self.model, "feature_names": self.feature_names}
        joblib.dump(data, self.model_path)
        logger.info(f"MinutesModel saved to {self.model_path}")

    def load(self) -> None:
        """Load model and feature names from disk."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        data = joblib.load(self.model_path)
        self.model = data["model"]
        self.feature_names = data["feature_names"]
        logger.info(f"MinutesModel loaded from {self.model_path}")

