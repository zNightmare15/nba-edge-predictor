"""Ensemble prediction logic."""

import numpy as np

class EnsemblePredictor:
    """Weighted ensemble combining multiple model predictions."""

    def __init__(self, lgbm_weight: float = 0.55, xgb_weight: float = 0.45):
        self.lgbm_weight = lgbm_weight
        self.xgb_weight = xgb_weight
        total = self.lgbm_weight + self.xgb_weight
        self.lgbm_weight /= total
        self.xgb_weight /= total

    def predict(self, lgbm_pred: np.ndarray, xgb_pred: np.ndarray) -> np.ndarray:
        return self.lgbm_weight * lgbm_pred + self.xgb_weight * xgb_pred

