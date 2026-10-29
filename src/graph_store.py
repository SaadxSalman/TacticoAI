"""In-memory knowledge graph (fallback when Neo4j unavailable)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class InMemoryGraphStore:
    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}  # id -> {label, props}
        self.edges: list[dict] = []  # {src, dst, type}

    def add_node(self, node_id: str, label: str, props: Dict[str, Any] | None = None) -> None:
        self.nodes[node_id] = {"label": label, "props": props or {}}

    def add_edge(self, src: str, dst: str, edge_type: str) -> None:
        self.edges.append({"src": src, "dst": dst, "type": edge_type})

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)

    def neighbors(self, node_id: str, edge_type: str | None = None) -> List[Dict[str, Any]]:
        out = []
        for e in self.edges:
            if e["src"] == node_id and (edge_type is None or e["type"] == edge_type):
                n = self.nodes.get(e["dst"])
                if n:
                    out.append({"id": e["dst"], "edge": e["type"], **n["props"], "label": n["label"]})
        return out

    def query_players_by_team(self, team_id: str) -> List[Dict[str, Any]]:
        out = []
        for nid, n in self.nodes.items():
            if n["label"] == "Player" and n["props"].get("team_id") == team_id:
                out.append({"player_id": nid, **n["props"]})
        return out

    def all_nodes(self, label: str | None = None) -> List[Dict[str, Any]]:
        out = []
        for nid, n in self.nodes.items():
            if label is None or n["label"] == label:
                out.append({"id": nid, "label": n["label"], **n["props"]})
        return out
