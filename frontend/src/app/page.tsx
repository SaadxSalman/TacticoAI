"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function Dashboard() {
  const [players, setPlayers] = useState<any[]>([]);
  const [teams, setTeams] = useState<any[]>([]);

  useEffect(() => {
    apiGet("/api/v1/players").then(setPlayers).catch(() => {});
    apiGet("/api/v1/teams").then(setTeams).catch(() => {});
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">TacticoAI Dashboard</h1>
      <p className="text-gray-400 mb-8">Agentic Graph-RAG sports intelligence platform</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Players Tracked</h3>
          <p className="text-3xl font-bold text-blue-400">{players.length}</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Teams</h3>
          <p className="text-3xl font-bold text-green-400">{teams.length}</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Knowledge Chunks</h3>
          <p className="text-3xl font-bold text-purple-400">16+</p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Ask</h2>
        <p className="text-gray-400 mb-4">Try: "How many sprints did Mohamed Salah make in the second half?" or "Find defensive weaknesses of Arsenal"</p>
        <a href="/query" className="inline-block px-4 py-2 bg-blue-600 rounded hover:bg-blue-500">Open AI Query</a>
      </div>
    </div>
  );
}
