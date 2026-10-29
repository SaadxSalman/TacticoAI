"""Bootstrap in-memory stores from seed data."""

from __future__ import annotations

import math
import random

from src.data import TEAMS, PLAYERS, GAMES, KNOWLEDGE_CHUNKS, SPRINTS
from src.vector_store import InMemoryVectorStore
from src.graph_store import InMemoryGraphStore


def _dummy_embedding(text: str, dim: int = 64) -> list[float]:
    # Deterministic pseudo-embedding based on char codes (for demo retrieval)
    vec = [0.0] * dim
    for i, ch in enumerate(text):
        vec[i % dim] += (ord(ch) % 31) / 31.0
    # normalize
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def build_vector_store() -> InMemoryVectorStore:
    store = InMemoryVectorStore()
    store.ensure_collection("knowledge")
    points = []
    for c in KNOWLEDGE_CHUNKS:
        points.append({
            "id": c["id"],
            "vector": _dummy_embedding(c["text"]),
            "payload": {
                "content": c["text"],
                "source": c["source"],
                "tags": c.get("tags", []),
                "text_snippet": c["text"][:80],
            },
        })
    # sprint telemetry as chunks
    for s in SPRINTS:
        txt = f"Player {s['player_id']} sprint in {s['period']} of game {s['game_id']}: speed {s['speed_kmh']} km/h, distance {s['distance_km']} km at minute {s['minute']}."
        points.append({
            "id": f"SP_{s['player_id']}_{s['game_id']}_{s['minute']}",
            "vector": _dummy_embedding(txt),
            "payload": {
                "content": txt,
                "source": "telemetry",
                "player_id": s["player_id"],
                "game_id": s["game_id"],
                "period": s["period"],
                "speed_kmh": s["speed_kmh"],
                "text_snippet": txt[:80],
            },
        })
    store.upsert("knowledge", points)
    return store


def build_graph_store() -> InMemoryGraphStore:
    g = InMemoryGraphStore()
    for t in TEAMS:
        g.add_node(t["team_id"], "Team", {"name": t["name"], "league": t["league"], "style": t["style"]})
    for p in PLAYERS:
        g.add_node(p["player_id"], "Player", {"name": p["name"], "team_id": p["team_id"], "position": p["position"], "age": p["age"], "nationality": p["nationality"]})
        g.add_edge(p["player_id"], p["team_id"], "PLAYS_FOR")
    for gm in GAMES:
        g.add_node(gm["game_id"], "Game", {"date": gm["date"], "home_team": gm["home_team"], "away_team": gm["away_team"], "location": gm["location"], "result": gm["result"]})
        g.add_edge(gm["home_team"], gm["game_id"], "PLAYED_IN")
        g.add_edge(gm["away_team"], gm["game_id"], "PLAYED_IN")
    # formations as weak nodes
    formations = {"T_LIV": "4-3-3", "T_MCI": "4-3-3", "T_ARS": "4-3-3", "T_CHE": "4-2-3-1"}
    for tid, f in formations.items():
        fid = f"FORM_{f}"
        if fid not in g.nodes:
            g.add_node(fid, "Formation", {"formation_name": f})
        g.add_edge(tid, fid, "USES_FORMATION")
    return g


VECTOR_STORE: InMemoryVectorStore = build_vector_store()
GRAPH_STORE: InMemoryGraphStore = build_graph_store()


def dummy_embedding(text: str, dim: int = 64) -> list[float]:
    return _dummy_embedding(text, dim)
