"""Inference engine to produce player stat projections."""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from src.utils.logger import logger
from src.models.minutes_model import MinutesModel
from src.models.stat_model import StatModel
from src.utils.constants import TARGET_STATS

class PredictionEngine:
    """Loads trained models and generates projections for players."""

    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = Path(model_dir)
        self.minutes_model = MinutesModel(model_dir=str(self.model_dir))
        self.stat_models: Dict[str, StatModel] = {}
        self._load_all()

    def _load_all(self) -> None:
        try:
            self.minutes_model.load()
            for stat in TARGET_STATS:
                model = StatModel(stat_name=stat, model_dir=str(self.model_dir))
                try:
                    model.load()
                    self.stat_models[stat] = model
                except FileNotFoundError:
                    logger.debug(f"Stat model for '{stat}' not found on disk yet.")
        except Exception as e:
            logger.warning(f"Could not load all model artifacts: {e}")

    def predict_features(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """Add projected stats and minutes columns to input dataframe."""
        df = feature_df.copy()

        # 1. Project minutes
        if self.minutes_model.model is not None:
            df["predicted_minutes"] = self.minutes_model.predict(df)
        else:
            df["predicted_minutes"] = df.get("minutes_roll_5", 30.0)

        # 2. Project each stat
        for stat, model in self.stat_models.items():
            df[f"proj_{stat}"] = model.predict(df)

        return df

    def predict_single_player(self, player_features: Dict[str, Any]) -> Dict[str, float]:
        """Project all stats for a single player feature dictionary."""
        df = pd.DataFrame([player_features])
        res_df = self.predict_features(df)
        projections = {}
        for col in res_df.columns:
            if col.startswith("proj_") or col == "predicted_minutes":
                projections[col] = float(res_df[col].iloc[0])
        return projections

