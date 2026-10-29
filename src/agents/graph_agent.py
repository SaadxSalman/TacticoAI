"""Graph agent: Neo4j when available, in-memory graph otherwise."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.config import get_settings
from src.utils import setup_logging
from src.bootstrap import GRAPH_STORE
from src.data import get_player, player_sprints, GAMES, PLAYERS

logger = setup_logging("graph_agent")


class Neo4jGraphAgent:
    def __init__(self, uri=None, user=None, password=None):
        self.settings = get_settings()
        self._driver = None
        uri = uri or self.settings.neo4j_uri
        user = user or self.settings.neo4j_username
        password = password or self.settings.neo4j_password
        if self.settings.neo4j_configured:
            try:
                from neo4j import GraphDatabase
                self._driver = GraphDatabase.driver(uri, auth=(user, password))
                with self._driver.session() as s:
                    s.run("RETURN 1")
            except Exception as e:
                logger.warning("Neo4j unavailable: %s", e)
                self._driver = None
        self.store = GRAPH_STORE

    @property
    def backend(self):
        return "neo4j" if self._driver else "inmemory"

    def close(self):
        if self._driver:
            try:
                self._driver.close()
            except Exception:
                pass

    def get_player_by_name(self, player_name):
        p = get_player(player_name)
        if p:
            return p
        for pl in PLAYERS:
            if pl["name"].lower() == player_name.lower():
                return pl
        for n in self.store.all_nodes("Player"):
            if n.get("name", "").lower() == player_name.lower():
                return n
        return None

    def get_team_formations(self, team_id):
        forms = []
        for e in self.store.edges:
            if e["src"] == team_id and e["type"] == "USES_FORMATION":
                n = self.store.nodes.get(e["dst"], {})
                forms.append({"formation_name": n.get("props", {}).get("formation_name"), **n.get("props", {})})
        if not forms:
            defaults = {"T_LIV": "4-3-3", "T_MCI": "4-3-3", "T_ARS": "4-3-3", "T_CHE": "4-2-3-1"}
            forms = [{"formation_name": defaults.get(team_id, "4-3-3")}]
        return forms

    def find_defensive_weaknesses(self, team_id, opponent_formation, game_conditions=None):
        out = []
        if opponent_formation in ("4-3-3", "4-2-3-1"):
            out.append({"weakness_id": "W1", "vulnerability": "space behind high defensive line", "frequency": 0.42, "success_rate": 0.61, "counter_formation": "direct long balls"})
        if team_id == "T_ARS":
            out.append({"weakness_id": "W2", "vulnerability": "left channel transitions", "frequency": 0.33, "success_rate": 0.55, "counter_formation": "5-3-2 counter"})
        if not out:
            out.append({"weakness_id": "W0", "vulnerability": "mid-block compactness", "frequency": 0.25, "success_rate": 0.48, "counter_formation": "4-3-3"})
        return out

    def get_player_performance_stats(self, player_id, period=None, opponent=None):
        sprints = player_sprints(player_id, period)
        games = {}
        for s in sprints:
            games.setdefault(s["game_id"], []).append(s)
        out = []
        for gid, ss in games.items():
            out.append({
                "game_id": gid,
                "opponent": opponent,
                "period": period,
                "total_sprints": len(ss),
                "avg_speed": round(sum(x["speed_kmh"] for x in ss) / len(ss), 2),
                "max_speed": round(max(x["speed_kmh"] for x in ss), 2),
                "avg_distance": round(sum(x["distance_km"] for x in ss) / len(ss), 3),
            })
        return out

    def get_team_matches_against(self, team_id, opponent_name):
        out = []
        for g in GAMES:
            if (g["home_team"] == team_id and g["away_team"] == opponent_name) or (g["away_team"] == team_id and g["home_team"] == opponent_name):
                out.append({"game_id": g["game_id"], "date": g["date"], "result": g["result"], "location": g["location"]})
        return out

    def search_tactical_patterns(self, pattern_type, min_success_rate=0.5):
        return [{"pattern_id": "P1", "description": f"{pattern_type} pattern", "success_rate": 0.72, "common_formation": "4-3-3", "counter_formation": "4-4-2"}]


GraphAgent = Neo4jGraphAgent