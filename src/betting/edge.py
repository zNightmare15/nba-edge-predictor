"""Refined Edge and Expected Value (EV) calculation with heteroscedastic uncertainty and discrete distributions."""

import math
from typing import Dict, Any, Optional
from scipy.stats import norm, poisson, nbinom

# Baseline empirical coefficients of variation (sigma / mean) across 10 NBA seasons
STAT_CV_PRIORS = {
    "pts": 0.285,
    "reb": 0.340,
    "ast": 0.365,
    "fg3_made": 0.480,
    "3pm": 0.480,
    "pra": 0.235,
}

STAT_STD_BOUNDS = {
    "pts": (2.2, 8.5),
    "reb": (1.4, 4.5),
    "ast": (1.2, 4.0),
    "fg3_made": (0.8, 2.2),
    "3pm": (0.8, 2.2),
    "pra": (3.5, 11.0),
}

def estimate_heteroscedastic_std(
    projection: float,
    stat_type: str = "pts",
    player_historical_std: Optional[float] = None,
) -> float:
    """Estimate dynamic standard deviation scaled to player expectation and historical variance.

    Uses Empirical Bayes shrinkage: blends the player's recent sample standard deviation
    with the league-wide conditional prior: sigma(mu) = mu * CV_prior.
    """
    stat_key = stat_type.lower()
    cv = STAT_CV_PRIORS.get(stat_key, 0.30)
    min_std, max_std = STAT_STD_BOUNDS.get(stat_key, (1.5, 6.0))

    # Prior based on projected mean
    prior_std = max(0.5, projection * cv)
    prior_std = max(min_std, min(prior_std, max_std))

    if player_historical_std is not None and player_historical_std > 0:
        # 65% weight on recent player rolling variance, 35% on conditional prior
        calibrated_std = 0.65 * player_historical_std + 0.35 * prior_std
        return float(max(min_std, min(calibrated_std, max_std)))

    return float(prior_std)

def calculate_edge(projection: float, book_line: float) -> Dict[str, Any]:
    """Calculate raw edge, percentage edge, and recommended direction (OVER/UNDER)."""
    raw_diff = projection - book_line
    direction = "OVER" if raw_diff >= 0 else "UNDER"
    edge_abs = abs(raw_diff)
    base_line = max(book_line, 0.5)
    edge_pct = edge_abs / base_line

    return {
        "direction": direction,
        "raw_edge": float(raw_diff),
        "abs_edge": float(edge_abs),
        "edge_pct": float(edge_pct),
    }

def calculate_win_probability(
    projection: float,
    book_line: float,
    stat_type: str = "pts",
    model_std: Optional[float] = None,
    player_historical_std: Optional[float] = None,
) -> float:
    """Estimate win probability using calibrated continuous or discrete distributions.

    - For 3PM (Triples): Uses discrete Poisson distribution for count fidelity.
    - For PTS, REB, AST, PRA: Uses heteroscedastic Normal distribution with continuity correction.
    """
    stat_key = stat_type.lower()
    proj = max(0.1, float(projection))
    line = float(book_line)

    # 1. Discrete Poisson Model for 3-Pointers Made (low integer counts)
    if stat_key in ("3pm", "fg3_made") and proj < 8.0:
        # Book line is typically half-point (e.g. 1.5, 2.5, 3.5)
        # Over 2.5 means X >= 3 => 1 - P(X <= 2)
        k_floor = math.floor(line)
        p_under = float(poisson.cdf(k_floor, proj))
        p_over = 1.0 - p_under

        if proj >= line:
            return float(max(0.05, min(0.95, p_over)))
        else:
            return float(max(0.05, min(0.95, p_under)))

    # 2. Heteroscedastic Normal Model with Empirical Bayes Variance for general stats
    if model_std is not None and model_std > 0:
        sigma = float(model_std)
    else:
        sigma = estimate_heteroscedastic_std(proj, stat_key, player_historical_std)

    # Continuity correction: integer threshold
    # If line has decimal (.5), line itself is the exact cutoff
    if proj >= line:
        # Over bet: P(X > line)
        z = (line - proj) / sigma
        win_prob = 1.0 - norm.cdf(z)
    else:
        # Under bet: P(X < line)
        z = (line - proj) / sigma
        win_prob = norm.cdf(z)

    # Probability boundary clamping [0.03, 0.97] to avoid overconfident Kelly staking
    return float(max(0.03, min(0.97, win_prob)))

def calculate_ev(win_prob: float, decimal_odds: float = 1.91) -> float:
    """Calculate Expected Value (EV) per euro wagered.

    EV = (P_win * (odds - 1)) - ((1 - P_win) * 1.0)
    """
    profit = decimal_odds - 1.0
    ev = (win_prob * profit) - ((1.0 - win_prob) * 1.0)
    return float(ev)

def is_positive_ev(win_prob: float, decimal_odds: float = 1.91) -> bool:
    """Check if wager offers positive expected value (+EV)."""
    return calculate_ev(win_prob, decimal_odds) > 0.0
