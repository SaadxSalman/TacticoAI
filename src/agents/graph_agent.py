"""Graph Agent - Neo4j Cypher Generation and GraphRAG Queries"""

from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Result


class Neo4jGraphAgent:
    """Agent for generating and executing Cypher queries against Neo4j knowledge graph."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
    
    def _execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """Execute a Cypher query and return results."""
        with self.driver.session() as session:
            result: Result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def get_player_by_name(self, player_name: str) -> Optional[Dict]:
        """Get player node by name."""
        query = """
        MATCH (p:Player {name: $player_name})
        RETURN p.player_id as player_id, p.name as name, 
               p.team_id as team_id, p.position as position,
               p.age as age, p.nationality as nationality
        """
        results = self._execute_query(query, {"player_name": player_name})
        return results[0] if results else None
    
    def get_team_formations(self, team_id: str) -> List[Dict]:
        """Get all formations used by a team."""
        query = """
        MATCH (t:Team {team_id: $team_id})-[:USES]->(f:Formation)
        RETURN f.formation_name as formation_name, 
               f.formation_description as description,
               f.player_roles as player_roles
        """
        return self._execute_query(query, {"team_id": team_id})
    
    def find_defensive_weaknesses(
        self, 
        team_id: str, 
        opponent_formation: str,
        game_conditions: Dict[str, Any] = None
    ) -> List[Dict]:
        """Find defensive weaknesses of a team against a specific formation."""
        query = """
        MATCH (t:Team {team_id: $team_id})-[:USES_FORMATION]->(f:Formation)-[:COUNTERS]->(w:Weakness)
        WHERE f.formation_name = $opponent_formation
        RETURN w.weakness_id as weakness_id,
               w.area_of_vulnerability as vulnerability,
               w.frequency_of_exploitation as frequency,
               w.success_rate as success_rate,
               w.counter_formation as counter_formation
        """
        return self._execute_query(query, {
            "team_id": team_id,
            "opponent_formation": opponent_formation
        })
    
    def get_player_performance_stats(
        self, 
        player_id: str, 
        period: str = None,
        opponent: str = None
    ) -> List[Dict]:
        """Get player performance statistics with optional filtering."""
        query = """
        MATCH (p:Player {player_id: $player_id})<-[:PLAYER_IN]-(g:Game)-[s:SPRINT]->(stats:SprintStats)
        WHERE g.period = $period OR $period IS NULL
        AND g.opponent = $opponent OR $opponent IS NULL
        RETURN g.game_id as game_id,
               g.opponent as opponent,
               g.period as period,
               COUNT(s) as total_sprints,
               AVG(s.speed_kmh) as avg_speed,
               MAX(s.speed_kmh) as max_speed,
               AVG(s.distance_km) as avg_distance
        """
        return self._execute_query(query, {
            "player_id": player_id,
            "period": period,
            "opponent": opponent
        })
    
    def get_team_matches_against(
        self, 
        team_id: str, 
        opponent_name: str
    ) -> List[Dict]:
        """Get all matches between two teams."""
        query = """
        MATCH (t1:Team {team_id: $team_id})<-[:PLAYS_FOR]-(p1:Player)-[:PLAYED_IN]->(g:Game)-[:BETWEEN]->(t2:Team {team_id: $opponent_name})
        RETURN g.game_id as game_id,
               g.date as date,
               g.result as result,
               g.location as location
        """
        return self._execute_query(query, {
            "team_id": team_id,
            "opponent_name": opponent_name
        })
    
    def search_tactical_patterns(
        self, 
        pattern_type: str,
        min_success_rate: float = 0.5
    ) -> List[Dict]:
        """Search for tactical patterns in the knowledge graph."""
        query = """
        MATCH (p:Pattern {pattern_type: $pattern_type, success_rate >= $min_rate})
        RETURN p.pattern_id as pattern_id,
               p.description as description,
               p.success_rate as success_rate,
               p.common_formation as common_formation,
               p.counter_formation as counter_formation
        ORDER BY p.success_rate DESC
        """
        return self._execute_query(query, {
            "pattern_type": pattern_type,
            "min_rate": min_success_rate
        })