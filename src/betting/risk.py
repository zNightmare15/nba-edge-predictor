"""Multi-factor risk assessment scoring engine."""

from typing import Dict, Any, Tuple

def calculate_risk_score(game_context: Dict[str, Any]) -> Tuple[str, float]:
    """Calculate composite risk score and assign risk tier (LOW, MEDIUM, HIGH).

    Parameters
    ----------
    game_context : dict
        Context dictionary containing spread, injury status, consistency,
        rest, teammate status, and edge metrics.

    Returns
    -------
    tuple of (risk_level: str, risk_score: float)
    """
    score = 0.0

    # Factor 1: Blowout potential (weight: 2.0)
    abs_spread = abs(float(game_context.get("spread", 0.0)))
    if abs_spread > 12.0:
        score += 2.0  # High blowout risk: starters might sit during 4th quarter
    elif abs_spread > 8.0:
        score += 1.2
    elif abs_spread > 5.0:
        score += 0.6

    # Factor 2: Player injury / availability status (weight: 2.0)
    status = str(game_context.get("player_status", "Available")).capitalize()
    if status in ("Questionable", "Gtd", "Doubtful"):
        score += 2.0
    elif status == "Probable":
        score += 0.5

    # Factor 3: Minutes consistency (weight: 1.5)
    min_std = float(game_context.get("minutes_std_10", 3.0))
    if min_std > 6.0:
        score += 1.5
    elif min_std > 3.5:
        score += 0.75

    # Factor 4: Stat consistency (weight: 1.5) - coefficient of variation
    stat_std = float(game_context.get("stat_std_10", 2.0))
    stat_roll = float(game_context.get("stat_roll_10", 10.0))
    cv = stat_std / max(stat_roll, 0.1)
    if cv > 0.40:
        score += 1.5
    elif cv > 0.25:
        score += 0.75

    # Factor 5: Back-to-back schedule (weight: 1.0)
    if bool(game_context.get("is_second_of_b2b", False)):
        score += 1.0
    elif bool(game_context.get("is_b2b", False)):
        score += 0.5

    # Factor 6: Model edge magnitude (weight: 1.0, inverse risk)
    edge_pct = float(game_context.get("edge_pct", 0.10))
    if edge_pct < 0.05:
        score += 1.0  # Thin edge has high variance risk
    elif edge_pct < 0.10:
        score += 0.5

    # Factor 7: Key teammate availability (weight: 0.5)
    teammates_out = int(game_context.get("key_teammates_out", 0))
    if teammates_out >= 2:
        score += 0.5
    elif teammates_out == 1:
        score += 0.25

    # Factor 8: Historical matchup experience (weight: 0.5)
    times_played = int(game_context.get("times_played_opp_this_season", 1))
    if times_played == 0:
        score += 0.5

    # Determine classification tier
    if score <= 2.5:
        risk_level = "LOW"
    elif score <= 5.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return (risk_level, round(score, 2))

