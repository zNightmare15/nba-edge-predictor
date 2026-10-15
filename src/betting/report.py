"""Daily bet report generation and formatting."""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import pandas as pd
from rich.console import Console
from rich.table import Table
from src.utils.logger import logger
from src.betting.edge import calculate_edge, calculate_win_probability, calculate_ev
from src.betting.risk import calculate_risk_score
from src.betting.kelly import calculate_stake

@dataclass
class BetRecommendation:
    player_id: int
    player_name: str
    team: str
    opponent: str
    stat_type: str
    projection: float
    book_line: float
    book_odds: float
    direction: str          # OVER or UNDER
    raw_edge: float
    edge_pct: float
    win_prob: float
    ev: float
    risk_level: str         # LOW, MEDIUM, HIGH
    risk_score: float
    suggested_stake: float  # In EUR

def generate_recommendations(
    projections: List[Dict[str, Any]],
    bankroll: float = 1000.0,
    kelly_frac: float = 0.25,
    min_edge_pct: float = 0.03,
) -> List[BetRecommendation]:
    """Generate filtered and sorted bet recommendations from projections and lines."""
    recommendations: List[BetRecommendation] = []

    for item in projections:
        proj = float(item.get("projection", 0.0))
        line = float(item.get("book_line", 0.0))
        odds = float(item.get("book_odds", 1.91))
        stat = str(item.get("stat_type", "pts")).lower()

        edge_info = calculate_edge(proj, line)
        if edge_info["edge_pct"] < min_edge_pct:
            continue

        win_prob = calculate_win_probability(proj, line, stat_type=stat)
        ev = calculate_ev(win_prob, odds)
        if ev <= 0.0:
            continue

        risk_level, risk_score = calculate_risk_score(item)
        stake = calculate_stake(win_prob, odds, bankroll=bankroll, fraction=kelly_frac)

        rec = BetRecommendation(
            player_id=int(item.get("player_id", 0)),
            player_name=str(item.get("player_name", "Unknown")),
            team=str(item.get("team", "")),
            opponent=str(item.get("opponent", "")),
            stat_type=stat.upper(),
            projection=round(proj, 1),
            book_line=round(line, 1),
            book_odds=odds,
            direction=edge_info["direction"],
            raw_edge=round(edge_info["raw_edge"], 1),
            edge_pct=round(edge_info["edge_pct"] * 100, 1),
            win_prob=round(win_prob * 100, 1),
            ev=round(ev, 3),
            risk_level=risk_level,
            risk_score=risk_score,
            suggested_stake=stake,
        )
        recommendations.append(rec)

    # Sort by raw edge magnitude descending
    recommendations.sort(key=lambda r: abs(r.raw_edge), reverse=True)
    return recommendations

def print_console_report(recommendations: List[BetRecommendation]) -> None:
    """Print an attractive formatted table to the terminal."""
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    console = Console(highlight=False)
    table = Table(title="NBA Player Prop Bet Recommendations (bet365 / Winamax)", header_style="bold cyan")

    table.add_column("Player", style="bold white")
    table.add_column("Matchup", style="dim")
    table.add_column("Stat", justify="center")
    table.add_column("Proj", justify="right")
    table.add_column("Line", justify="right")
    table.add_column("Pick", justify="center", style="bold yellow")
    table.add_column("Edge %", justify="right")
    table.add_column("Win Prob", justify="right")
    table.add_column("Risk", justify="center")
    table.add_column("Stake (€)", justify="right", style="bold green")

    risk_colors = {"LOW": "[green]LOW[/green]", "MEDIUM": "[yellow]MED[/yellow]", "HIGH": "[red]HIGH[/red]"}

    for r in recommendations:
        risk_badge = risk_colors.get(r.risk_level, r.risk_level)
        table.add_row(
            r.player_name,
            f"{r.team} vs {r.opponent}",
            r.stat_type,
            str(r.projection),
            str(r.book_line),
            f"{r.direction} {r.book_line}",
            f"{r.edge_pct}%",
            f"{r.win_prob}%",
            risk_badge,
            f"€{r.suggested_stake:.2f}",
        )

    console.print(table)

