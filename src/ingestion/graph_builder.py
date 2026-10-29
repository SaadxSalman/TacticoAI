"""Graph Builder - Neo4j Schema Populator"""

from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase


class Neo4jGraphBuilder:
    """Builds and populates the Neo4j knowledge graph from sports data."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()

    def _execute_write(self, query: str, parameters: Dict[str, Any] = None) -> Any:
        """Execute a write query against Neo4j."""
        with self.driver.session() as session:
            return session.run(query, parameters or {}).data()

    def create_schema_indexes(self) -> None:
        """Create Neo4j schema indexes for performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (p:Player) ON (p.name)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Player) ON (p.player_id)",
            "CREATE INDEX IF NOT EXISTS FOR (t:Team) ON (t.team_id)",
            "CREATE INDEX IF NOT EXISTS FOR (t:Team) ON (t.name)",
        ]

        for idx in indexes:
            self._execute_write(idx)

    def create_player_node(
        self, player_id: str, name: str, team_id: str, position: str, age: int = None
    ) -> None:
        """Create a Player node."""
        query = (
            "MERGE (p:Player {player_id: $player_id}) "
            "ON CREATE SET p.name = $name, p.team_id = $team_id, p.position = $position "
            "ON MATCH SET p.name = $name"
        )
        self._execute_write(
            query,
            {"player_id": player_id, "name": name, "team_id": team_id, "position": position},
        )

    def create_team_node(self, team_id: str, name: str) -> None:
        """Create a Team node."""
        query = "MERGE (t:Team {team_id: $team_id}) ON CREATE SET t.name = $name"
        self._execute_write(query, {"team_id": team_id, "name": name})

    def create_game_node(self, game_id: str, date: str, home_team: str, away_team: str) -> None:
        """Create a Game node."""
        query = (
            "MERGE (g:Game {game_id: $game_id}) "
            "ON CREATE SET g.date = $date, g.home_team = $home_team, g.away_team = $away_team "
            "ON MATCH SET g.date = $date"
        )
        self._execute_write(
            query,
            {"game_id": game_id, "date": date, "home_team": home_team, "away_team": away_team},
        )

    def connect_player_to_team(self, player_id: str, team_id: str) -> None:
        """Connect player to team."""
        query = (
            "MATCH (p:Player {player_id: $player_id}), (t:Team {team_id: $team_id}) "
            "MERGE (p)-[:PLAYS_FOR]->(t)"
        )
        self._execute_write(query, {"player_id": player_id, "team_id": team_id})