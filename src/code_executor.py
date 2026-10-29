"""Safe code execution engine for analytical/statistical queries."""

from __future__ import annotations

import io
import contextlib
import traceback
from typing import Any, Dict


class CodeExecutionEngine:
    """Executes Python code in a restricted namespace with captured stdout."""

    ALLOWED_BUILTINS = {
        "len", "sum", "min", "max", "round", "abs", "sorted", "range",
        "enumerate", "zip", "list", "dict", "set", "tuple", "float", "int",
        "str", "bool", "print", "map", "filter",
    }

    def execute(self, code: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        namespace: dict[str, Any] = {}
        if context:
            namespace.update(context)
        # Provide safe builtins
        import builtins
        safe_builtins = {k: getattr(builtins, k) for k in self.ALLOWED_BUILTINS if hasattr(builtins, k)}
        namespace["__builtins__"] = safe_builtins

        stdout_buf = io.StringIO()
        result: Dict[str, Any] = {"success": False, "stdout": "", "result": None, "error": None}
        try:
            with contextlib.redirect_stdout(stdout_buf):
                exec(compile(code, "<tacticoai>", "exec"), namespace)
            result["success"] = True
            result["stdout"] = stdout_buf.getvalue()
            # expose a conventional 'result' variable if set
            if "result" in namespace:
                result["result"] = namespace["result"]
            elif "answer" in namespace:
                result["result"] = namespace["answer"]
        except Exception:
            result["error"] = traceback.format_exc()
            result["stdout"] = stdout_buf.getvalue()
        return result

    def compute_player_stats(self, player_id: str, period: str | None = None) -> Dict[str, Any]:
        from src.data import player_sprints
        sprints = player_sprints(player_id, period)
        if not sprints:
            return {"player_id": player_id, "count": 0, "avg_speed": 0.0, "max_speed": 0.0, "total_distance": 0.0}
        speeds = [s["speed_kmh"] for s in sprints]
        dists = [s["distance_km"] for s in sprints]
        code = """
count = len(speeds)
avg_speed = round(sum(speeds)/count, 2)
max_speed = round(max(speeds), 2)
total_distance = round(sum(dists), 3)
result = {'count': count, 'avg_speed': avg_speed, 'max_speed': max_speed, 'total_distance': total_distance}
"""
        res = self.execute(code, {"speeds": speeds, "dists": dists})
        out = res.get("result") or {}
        out["player_id"] = player_id
        out["period"] = period
        out["success"] = res["success"]
        return out
