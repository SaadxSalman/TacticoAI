import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.engine.rag_pipeline import AgenticRAGPipeline


def test_pipeline_query():
    p = AgenticRAGPipeline()
    res = p.process_query("How many sprints did Mohamed Salah make in the second half?")
    assert "response" in res
    assert res["code_execution"]["player_id"] == "P_SALAH"
    assert res["code_execution"]["stats"]["count"] == 1
    p.close()


def test_router():
    from src.agents.router import route_query
    r = route_query("injury risk for Salah")
    assert r.intent.value == "injury_risk"


def test_crag():
    from src.agents.evaluator import CRAGEvaluator
    ev = CRAGEvaluator()
    r = ev.evaluate("x", [])
    assert r["satisfied"] is False