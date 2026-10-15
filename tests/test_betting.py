"""Unit tests for edge, probability, risk assessment, and Kelly staking."""

import pytest
from src.betting.edge import calculate_edge, calculate_win_probability, calculate_ev, is_positive_ev
from src.betting.risk import calculate_risk_score
from src.betting.kelly import kelly_fraction, calculate_stake

def test_calculate_edge_over():
    res = calculate_edge(projection=32.0, book_line=28.5)
    assert res["direction"] == "OVER"
    assert res["raw_edge"] == 3.5
    assert res["edge_pct"] > 0.10

def test_calculate_edge_under():
    res = calculate_edge(projection=22.0, book_line=25.5)
    assert res["direction"] == "UNDER"
    assert res["raw_edge"] == -3.5
    assert res["edge_pct"] > 0.10

def test_win_probability_and_ev():
    # If projection is higher than line, win probability should be > 50%
    prob = calculate_win_probability(projection=32.0, book_line=28.5, stat_type="pts")
    assert prob > 0.50
    ev = calculate_ev(prob, decimal_odds=1.91)
    assert is_positive_ev(prob, decimal_odds=1.91) == (ev > 0)

def test_risk_score_low():
    # Competitive game, healthy player, consistent minutes
    ctx = {
        "spread": -2.5,
        "player_status": "Available",
        "minutes_std_10": 2.0,
        "stat_std_10": 3.0,
        "stat_roll_10": 30.0,
        "is_second_of_b2b": False,
        "edge_pct": 0.15,
        "key_teammates_out": 0,
        "times_played_opp_this_season": 2,
    }
    tier, score = calculate_risk_score(ctx)
    assert tier == "LOW"
    assert score <= 2.5

def test_risk_score_high_blowout_and_injury():
    # Massive spread (>12) + Questionable injury status
    ctx = {
        "spread": -16.5,
        "player_status": "Questionable",
        "minutes_std_10": 7.5,
        "stat_std_10": 10.0,
        "stat_roll_10": 20.0,
        "is_second_of_b2b": True,
        "edge_pct": 0.03,
        "key_teammates_out": 2,
        "times_played_opp_this_season": 0,
    }
    tier, score = calculate_risk_score(ctx)
    assert tier == "HIGH"
    assert score > 5.0

def test_kelly_stake():
    # 60% win prob at 1.91 odds has positive stake
    stake = calculate_stake(win_prob=0.60, decimal_odds=1.91, bankroll=1000.0, fraction=0.25)
    assert stake > 0.0
    # Stake should never exceed 5% cap (50.0)
    assert stake <= 50.0

    # 40% win prob at 1.91 odds has 0 stake
    stake_loss = calculate_stake(win_prob=0.40, decimal_odds=1.91, bankroll=1000.0)
    assert stake_loss == 0.0

def test_heteroscedastic_std_scaling():
    from src.betting.edge import estimate_heteroscedastic_std
    # Star player with 35 pts should have higher std than role player with 8 pts
    std_star = estimate_heteroscedastic_std(projection=35.0, stat_type="pts")
    std_role = estimate_heteroscedastic_std(projection=8.0, stat_type="pts")
    assert std_star > std_role
    assert std_role >= 2.2
    assert std_star <= 8.5

def test_poisson_3pm_probability():
    # 3PM should use discrete Poisson distribution
    prob_over = calculate_win_probability(projection=3.5, book_line=2.5, stat_type="3pm")
    prob_under = calculate_win_probability(projection=1.5, book_line=2.5, stat_type="3pm")
    assert prob_over > 0.50
    assert prob_under > 0.50

