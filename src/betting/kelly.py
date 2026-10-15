"""Kelly Criterion position sizing with fractional scaling."""

def kelly_fraction(win_prob: float, decimal_odds: float) -> float:
    """Calculate raw Kelly Criterion stake fraction.

    f* = (b * p - q) / b
    where:
    b = decimal_odds - 1 (net profit per unit staked)
    p = win probability
    q = 1 - p
    """
    b = decimal_odds - 1.0
    if b <= 0.0 or win_prob <= 0.0:
        return 0.0

    q = 1.0 - win_prob
    f = (b * win_prob - q) / b
    return max(0.0, float(f))

def calculate_stake(
    win_prob: float,
    decimal_odds: float,
    bankroll: float,
    fraction: float = 0.25,
    max_stake_pct: float = 0.05,
) -> float:
    """Calculate recommended bet stake using fractional Kelly Criterion.

    Parameters
    ----------
    win_prob : float
        Model estimated win probability (0.0 to 1.0).
    decimal_odds : float
        Bookmaker decimal odds (e.g. 1.91 for standard -110 lines).
    bankroll : float
        Current total bankroll in EUR.
    fraction : float, default 0.25
        Fractional Kelly multiplier (0.25 = quarter Kelly for lower volatility).
    max_stake_pct : float, default 0.05
        Maximum cap on single bet size as fraction of bankroll (default 5%).

    Returns
    -------
    float
        Stake amount rounded to two decimals.
    """
    raw_f = kelly_fraction(win_prob, decimal_odds)
    scaled_f = raw_f * fraction
    capped_f = min(scaled_f, max_stake_pct)
    stake = capped_f * bankroll
    return round(float(stake), 2)

