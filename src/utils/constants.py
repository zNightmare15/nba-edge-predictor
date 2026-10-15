"""Constants for the NBA betting system."""

from typing import Dict, List

# Target seasons for 10-year historical training through current/future
SEASONS: List[str] = [
    "2014-15",
    "2015-16",
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]

# All 30 active NBA teams with standard NBA ID and abbreviations
NBA_TEAMS: Dict[str, Dict[str, str | int]] = {
    "ATL": {"id": 1610612737, "name": "Atlanta Hawks", "city": "Atlanta", "conference": "East", "division": "Southeast"},
    "BOS": {"id": 1610612738, "name": "Boston Celtics", "city": "Boston", "conference": "East", "division": "Atlantic"},
    "BKN": {"id": 1610612751, "name": "Brooklyn Nets", "city": "Brooklyn", "conference": "East", "division": "Atlantic"},
    "CHA": {"id": 1610612766, "name": "Charlotte Hornets", "city": "Charlotte", "conference": "East", "division": "Southeast"},
    "CHI": {"id": 1610612741, "name": "Chicago Bulls", "city": "Chicago", "conference": "East", "division": "Central"},
    "CLE": {"id": 1610612739, "name": "Cleveland Cavaliers", "city": "Cleveland", "conference": "East", "division": "Central"},
    "DAL": {"id": 1610612742, "name": "Dallas Mavericks", "city": "Dallas", "conference": "West", "division": "Southwest"},
    "DEN": {"id": 1610612743, "name": "Denver Nuggets", "city": "Denver", "conference": "West", "division": "Northwest"},
    "DET": {"id": 1610612765, "name": "Detroit Pistons", "city": "Detroit", "conference": "East", "division": "Central"},
    "GSW": {"id": 1610612744, "name": "Golden State Warriors", "city": "Golden State", "conference": "West", "division": "Pacific"},
    "HOU": {"id": 1610612745, "name": "Houston Rockets", "city": "Houston", "conference": "West", "division": "Southwest"},
    "IND": {"id": 1610612754, "name": "Indiana Pacers", "city": "Indiana", "conference": "East", "division": "Central"},
    "LAC": {"id": 1610612746, "name": "LA Clippers", "city": "Los Angeles", "conference": "West", "division": "Pacific"},
    "LAL": {"id": 1610612747, "name": "Los Angeles Lakers", "city": "Los Angeles", "conference": "West", "division": "Pacific"},
    "MEM": {"id": 1610612763, "name": "Memphis Grizzlies", "city": "Memphis", "conference": "West", "division": "Southwest"},
    "MIA": {"id": 1610612748, "name": "Miami Heat", "city": "Miami", "conference": "East", "division": "Southeast"},
    "MIL": {"id": 1610612749, "name": "Milwaukee Bucks", "city": "Milwaukee", "conference": "East", "division": "Central"},
    "MIN": {"id": 1610612750, "name": "Minnesota Timberwolves", "city": "Minnesota", "conference": "West", "division": "Northwest"},
    "NOP": {"id": 1610612740, "name": "New Orleans Pelicans", "city": "New Orleans", "conference": "West", "division": "Southwest"},
    "NYK": {"id": 1610612752, "name": "New York Knicks", "city": "New York", "conference": "East", "division": "Atlantic"},
    "OKC": {"id": 1610612760, "name": "Oklahoma City Thunder", "city": "Oklahoma City", "conference": "West", "division": "Northwest"},
    "ORL": {"id": 1610612753, "name": "Orlando Magic", "city": "Orlando", "conference": "East", "division": "Southeast"},
    "PHI": {"id": 1610612755, "name": "Philadelphia 76ers", "city": "Philadelphia", "conference": "East", "division": "Atlantic"},
    "PHX": {"id": 1610612756, "name": "Phoenix Suns", "city": "Phoenix", "conference": "West", "division": "Pacific"},
    "POR": {"id": 1610612757, "name": "Portland Trail Blazers", "city": "Portland", "conference": "West", "division": "Northwest"},
    "SAC": {"id": 1610612758, "name": "Sacramento Kings", "city": "Sacramento", "conference": "West", "division": "Pacific"},
    "SAS": {"id": 1610612759, "name": "San Antonio Spurs", "city": "San Antonio", "conference": "West", "division": "Southwest"},
    "TOR": {"id": 1610612761, "name": "Toronto Raptors", "city": "Toronto", "conference": "East", "division": "Atlantic"},
    "UTA": {"id": 1610612762, "name": "Utah Jazz", "city": "Utah", "conference": "West", "division": "Northwest"},
    "WAS": {"id": 1610612764, "name": "Washington Wizards", "city": "Washington", "conference": "East", "division": "Southeast"},
}

TEAM_ID_TO_ABBR: Dict[int, str] = {data["id"]: abbr for abbr, data in NBA_TEAMS.items()}
TEAM_NAME_TO_ABBR: Dict[str, str] = {data["name"].lower(): abbr for abbr, data in NBA_TEAMS.items()}

TARGET_STATS = ["pts", "reb", "ast", "fg3_made", "pra"]

# Altitude effect: Denver altitude advantage
HIGH_ALTITUDE_TEAMS = {"DEN", "UTA"}

