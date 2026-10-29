"use client";

import { useState } from "react";
import { apiPost } from "../../lib/api";

export default function QueryPage() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  async function submit(e: any) {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    try {
      const r = await apiPost("/api/v1/query", { query: q, include_code_execution: true, include_video_timestamps: true });
      setResult(r);
    } catch (err: any) {
      setResult({ response: "Error: " + err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Ask TacticoAI</h1>
      <form onSubmit={submit} className="flex gap-3 mb-6">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="e.g. How many sprints did Salah make in the second half?"
          className="flex-1 px-4 py-2 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:border-blue-500"
        />
        <button type="submit" disabled={loading} className="px-6 py-2 bg-blue-600 rounded hover:bg-blue-500 disabled:opacity-50">
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {result && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-3">Answer</h2>
            <pre className="whitespace-pre-wrap text-gray-200">{result.response}</pre>
          </div>

          {result.code_execution && Object.keys(result.code_execution).length > 0 && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">Code Execution</h2>
              <pre className="text-sm text-green-300 bg-black/30 p-3 rounded">{JSON.stringify(result.code_execution, null, 2)}</pre>
            </div>
          )}

          {result.routing_decision && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">Routing Decision</h2>
              <pre className="text-sm text-gray-300">{JSON.stringify(result.routing_decision, null, 2)}</pre>
            </div>
          )}

          {result.crag_evaluation && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">CRAG Evaluation</h2>
              <pre className="text-sm text-gray-300">{JSON.stringify(result.crag_evaluation, null, 2)}</pre>
            </div>
          )}

          {result.sources && result.sources.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-3">Sources</h2>
              <ul className="space-y-2 text-sm text-gray-300">
                {result.sources.map((s: any, i: number) => (
                  <li key={i} className="border-b border-gray-800 pb-2">
                    <span className="text-blue-400">{s.source}</span> — score {Number(s.score).toFixed(2)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
