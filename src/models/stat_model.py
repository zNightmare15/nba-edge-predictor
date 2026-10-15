"""Per-stat prediction model combining LightGBM and XGBoost."""

from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd
from src.utils.logger import logger

class StatModel:
    """Predicts a specific player statistical metric (e.g. pts, reb, ast)."""

    def __init__(self, stat_name: str, model_dir: str = "data/models"):
        self.stat_name = stat_name.lower()
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.model_dir / f"{self.stat_name}_models.joblib"
        self.lgb_model = None
        self.xgb_model = None
        self.feature_names = None

    def _get_feature_columns(self, df: pd.DataFrame) -> list[str]:
        exclude = {
            "id", "season", "game_id", "game_date", "player_id", "player_name",
            "team_id", "team_abbr", "opponent_team_id", "opponent_team_abbr",
            "wl", "pts", "reb", "ast", "stl", "blk", "tov", "pra", "minutes",
            "fg_made", "fg_attempted", "fg3_made", "fg3_attempted", "ft_made", "ft_attempted",
            "oreb", "dreb", "plus_minus"
        }
        # Note: predicted_minutes SHOULD be in features if present
        return [c for c in df.columns if (c not in exclude or c == "predicted_minutes") and np.issubdtype(df[c].dtype, np.number)]

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """Train LightGBM and XGBoost models for this stat."""
        import lightgbm as lgb
        import xgboost as xgb
        from sklearn.metrics import mean_absolute_error, root_mean_squared_error

        self.feature_names = self._get_feature_columns(X_train)
        X_tr = X_train[self.feature_names]

        logger.info(f"Training StatModel [{self.stat_name.upper()}] with {len(self.feature_names)} features on {len(X_tr)} samples (Robust Huber Loss)...")

        # 1. LightGBM Regressor (Huber Loss: robust to blowout/injury outliers)
        self.lgb_model = lgb.LGBMRegressor(
            objective="huber",
            alpha=0.9,
            num_leaves=63,
            max_depth=7,
            learning_rate=0.03,
            n_estimators=800,
            min_child_samples=15,
            subsample=0.8,
            colsample_bytree=0.75,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
        )

        lgb_eval = [(X_val[self.feature_names], y_val)] if X_val is not None and y_val is not None else None
        lgb_callbacks = [lgb.early_stopping(50, verbose=False)] if lgb_eval else None
        self.lgb_model.fit(X_tr, y_train, eval_set=lgb_eval, callbacks=lgb_callbacks)

        # 2. XGBoost Regressor (Pseudo-Huber Loss)
        self.xgb_model = xgb.XGBRegressor(
            objective="reg:pseudohubererror",
            max_depth=6,
            learning_rate=0.03,
            n_estimators=800,
            min_child_weight=10,
            subsample=0.8,
            colsample_bytree=0.75,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
            early_stopping_rounds=50 if X_val is not None and y_val is not None else None,
        )

        xgb_eval = [(X_val[self.feature_names], y_val)] if X_val is not None and y_val is not None else None
        self.xgb_model.fit(
            X_tr,
            y_train,
            eval_set=xgb_eval,
            verbose=False,
        )

        metrics = {}
        self.optimal_lgb_weight = 0.55
        self.optimal_xgb_weight = 0.45

        if X_val is not None and y_val is not None:
            lgb_p = self.lgb_model.predict(X_val[self.feature_names])
            xgb_p = self.xgb_model.predict(X_val[self.feature_names])

            mae_lgb = float(mean_absolute_error(y_val, lgb_p))
            mae_xgb = float(mean_absolute_error(y_val, xgb_p))

            # Inverse-error dynamic weighting
            inv_lgb = 1.0 / max(mae_lgb, 1e-4)
            inv_xgb = 1.0 / max(mae_xgb, 1e-4)
            tot_inv = inv_lgb + inv_xgb
            self.optimal_lgb_weight = float(inv_lgb / tot_inv)
            self.optimal_xgb_weight = float(inv_xgb / tot_inv)

            ens_p = self.optimal_lgb_weight * lgb_p + self.optimal_xgb_weight * xgb_p

            metrics["lgb_val_mae"] = mae_lgb
            metrics["xgb_val_mae"] = mae_xgb
            metrics["ens_val_mae"] = float(mean_absolute_error(y_val, ens_p))
            metrics["ens_val_rmse"] = float(root_mean_squared_error(y_val, ens_p))
            metrics["optimal_lgb_weight"] = self.optimal_lgb_weight
            metrics["optimal_xgb_weight"] = self.optimal_xgb_weight

            logger.info(
                f"[{self.stat_name.upper()}] Val Ensemble MAE: {metrics['ens_val_mae']:.2f} "
                f"(Weights: LGBM={self.optimal_lgb_weight:.2f}, XGB={self.optimal_xgb_weight:.2f})"
            )

        # Store feature importances
        self.feature_importances_ = dict(
            sorted(
                zip(self.feature_names, self.lgb_model.feature_importances_),
                key=lambda x: x[1],
                reverse=True
            )[:15]
        )

        self.save()
        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate ensemble prediction using optimal calibrated weights."""
        if self.lgb_model is None or self.xgb_model is None:
            self.load()

        X_feats = X[self.feature_names] if self.feature_names else X
        lgb_p = self.lgb_model.predict(X_feats)
        xgb_p = self.xgb_model.predict(X_feats)

        w_lgb = getattr(self, "optimal_lgb_weight", 0.55)
        w_xgb = getattr(self, "optimal_xgb_weight", 0.45)
        pred = w_lgb * lgb_p + w_xgb * xgb_p
        return np.maximum(pred, 0.0)

    def save(self) -> None:
        data = {
            "lgb_model": self.lgb_model,
            "xgb_model": self.xgb_model,
            "feature_names": self.feature_names,
            "optimal_lgb_weight": getattr(self, "optimal_lgb_weight", 0.55),
            "optimal_xgb_weight": getattr(self, "optimal_xgb_weight", 0.45),
            "feature_importances_": getattr(self, "feature_importances_", {}),
        }
        joblib.dump(data, self.model_path)
        logger.info(f"StatModel [{self.stat_name}] saved to {self.model_path}")

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        data = joblib.load(self.model_path)
        self.lgb_model = data["lgb_model"]
        self.xgb_model = data["xgb_model"]
        self.feature_names = data["feature_names"]
        self.optimal_lgb_weight = data.get("optimal_lgb_weight", 0.55)
        self.optimal_xgb_weight = data.get("optimal_xgb_weight", 0.45)
        self.feature_importances_ = data.get("feature_importances_", {})
        logger.info(f"StatModel [{self.stat_name}] loaded from {self.model_path}")

