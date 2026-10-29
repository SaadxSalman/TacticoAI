"""Seed / demo sports data for TacticoAI (soccer)."""

from __future__ import annotations

from typing import Any, Dict, List


TEAMS: List[Dict[str, Any]] = [
    {"team_id": "T_LIV", "name": "Liverpool", "league": "Premier League", "style": "high-press, gegenpressing"},
    {"team_id": "T_MCI", "name": "Manchester City", "league": "Premier League", "style": "possession, positional play"},
    {"team_id": "T_ARS", "name": "Arsenal", "league": "Premier League", "style": "high line, inverted fullbacks"},
    {"team_id": "T_CHE", "name": "Chelsea", "league": "Premier League", "style": "transitional, counter-attack"},
]

PLAYERS: List[Dict[str, Any]] = [
    {"player_id": "P_SALAH", "name": "Mohamed Salah", "team_id": "T_LIV", "position": "RW", "age": 32, "nationality": "Egypt"},
    {"player_id": "P_VVD", "name": "Virgil van Dijk", "team_id": "T_LIV", "position": "CB", "age": 33, "nationality": "Netherlands"},
    {"player_id": "P_TAA", "name": "Trent Alexander-Arnold", "team_id": "T_LIV", "position": "RB", "age": 26, "nationality": "England"},
    {"player_id": "P_HAALAND", "name": "Erling Haaland", "team_id": "T_MCI", "position": "ST", "age": 24, "nationality": "Norway"},
    {"player_id": "P_DEBRUYNE", "name": "Kevin De Bruyne", "team_id": "T_MCI", "position": "CM", "age": 33, "nationality": "Belgium"},
    {"player_id": "P_SAKA", "name": "Bukayo Saka", "team_id": "T_ARS", "position": "RW", "age": 23, "nationality": "England"},
    {"player_id": "P_ODEGAARD", "name": "Martin Odegaard", "team_id": "T_ARS", "position": "CAM", "age": 26, "nationality": "Norway"},
    {"player_id": "P_PALMER", "name": "Cole Palmer", "team_id": "T_CHE", "position": "CAM", "age": 22, "nationality": "England"},
]

GAMES: List[Dict[str, Any]] = [
    {"game_id": "G_001", "date": "2024-09-14", "home_team": "T_LIV", "away_team": "T_MCI", "location": "Anfield", "result": "1-1", "period_stats": {"first_half": {"sprints": 48}, "second_half": {"sprints": 52}}},
    {"game_id": "G_002", "date": "2024-10-05", "home_team": "T_ARS", "away_team": "T_CHE", "location": "Emirates", "result": "2-1", "period_stats": {"first_half": {"sprints": 40}, "second_half": {"sprints": 45}}},
    {"game_id": "G_003", "date": "2024-10-20", "home_team": "T_MCI", "away_team": "T_ARS", "location": "Etihad", "result": "2-2", "period_stats": {"first_half": {"sprints": 55}, "second_half": {"sprints": 60}}},
]
SPRINTS: List[Dict[str, Any]] = [
    {"player_id": "P_SALAH", "game_id": "G_001", "period": "second_half", "speed_kmh": 33.4, "distance_km": 0.12, "minute": 67},
    {"player_id": "P_SALAH", "game_id": "G_001", "period": "first_half", "speed_kmh": 31.2, "distance_km": 0.10, "minute": 23},
    {"player_id": "P_HAALAND", "game_id": "G_001", "period": "second_half", "speed_kmh": 34.1, "distance_km": 0.14, "minute": 78},
    {"player_id": "P_SAKA", "game_id": "G_002", "period": "second_half", "speed_kmh": 32.0, "distance_km": 0.11, "minute": 81},
    {"player_id": "P_PALMER", "game_id": "G_002", "period": "first_half", "speed_kmh": 30.5, "distance_km": 0.09, "minute": 34},
    {"player_id": "P_DEBRUYNE", "game_id": "G_003", "period": "first_half", "speed_kmh": 29.8, "distance_km": 0.08, "minute": 19},
    {"player_id": "P_ODEGAARD", "game_id": "G_003", "period": "second_half", "speed_kmh": 31.0, "distance_km": 0.10, "minute": 55},
]

WORKLOAD: List[Dict[str, Any]] = [
    {"player_id": "P_SALAH", "avg_minutes": 84, "recent_injuries": 1, "load_index": 78},
    {"player_id": "P_HAALAND", "avg_minutes": 90, "recent_injuries": 0, "load_index": 88},
    {"player_id": "P_VVD", "avg_minutes": 90, "recent_injuries": 2, "load_index": 82},
    {"player_id": "P_SAKA", "avg_minutes": 76, "recent_injuries": 0, "load_index": 65},
    {"player_id": "P_DEBRUYNE", "avg_minutes": 60, "recent_injuries": 1, "load_index": 55},
    {"player_id": "P_PALMER", "avg_minutes": 88, "recent_injuries": 0, "load_index": 80},
]

KNOWLEDGE_CHUNKS: List[Dict[str, Any]] = [
    {"id": "K_001", "text": "Liverpool's 4-3-3 high-press system relies on coordinated pressing triggers when the opponent plays a back pass to the goalkeeper. Salah and the front three initiate the press while the midfield line steps up.", "source": "tactical_playbook", "tags": ["formation", "tactics", "pressing"]},
    {"id": "K_002", "text": "Manchester City's 4-3-3 positional play uses inverted fullbacks to create overloads in midfield. Haaland stays high and central as a reference point.", "source": "tactical_playbook", "tags": ["formation", "tactics", "possession"]},
    {"id": "K_003", "text": "To counter a high defensive line, teams exploit the space behind with through balls and diagonal runs. Arsenal's high line is vulnerable to fast transitions and long balls over the top.", "source": "coaching_manual", "tags": ["defensive_weakness", "counter"]},
    {"id": "K_004", "text": "Player load management: high-intensity sprints above 30 km/h increase hamstring strain risk. Players with prior muscle injuries require 48-72h recovery between high-load sessions.", "source": "sports_science", "tags": ["injury", "load", "fatigue"]},
    {"id": "K_005", "text": "Second-half performance often declines due to fatigue; teams that rotate midfielders at 60-70 minutes maintain pressing intensity. Substitution timing is a key tactical lever.", "source": "coaching_manual", "tags": ["tactics", "substitution"]},
    {"id": "K_006", "text": "Arsenal under Arteta uses a 4-3-3 with Odegaard as a free 8, dropping between lines. Saka provides width and 1v1 threat on the right flank.", "source": "tactical_playbook", "tags": ["formation", "tactics"]},
    {"id": "K_007", "text": "Chelsea's transitional style exploits counter-attacks through Palmer as a creative hub. Defensive compactness in a mid-block is preferred against possession teams.", "source": "tactical_playbook", "tags": ["formation", "tactics"]},
    {"id": "K_008", "text": "Referee transcript: Match G_001 saw 24 fouls, 4 yellow cards, and one penalty awarded. High-intensity derby atmosphere contributed to elevated foul count.", "source": "referee_transcript", "tags": ["referee", "incidents"]},
]


def get_player(player_id: str) -> Dict[str, Any] | None:
    for p in PLAYERS:
        if p["player_id"] == player_id:
            return p
    return None


def get_team(team_id: str) -> Dict[str, Any] | None:
    for t in TEAMS:
        if t["team_id"] == team_id:
            return t
    return None


def player_sprints(player_id: str, period: str | None = None) -> List[Dict[str, Any]]:
    out = [s for s in SPRINTS if s["player_id"] == player_id]
    if period:
        out = [s for s in out if s["period"] == period]
    return out


def workload_for(player_id: str) -> Dict[str, Any] | None:
    for w in WORKLOAD:
        if w["player_id"] == player_id:
            return w
    return None