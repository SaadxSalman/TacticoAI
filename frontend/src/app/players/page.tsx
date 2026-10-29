"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

export default function PlayersPage() {
  const [players, setPlayers] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    apiGet("/api/v1/players").then(setPlayers).catch(() => {});
  }, []);

  async function loadStats(p: any) {
    setSelected(p);
    const s = await apiGet(`/api/v1/players/${p.player_id}/statistics`);
    setStats(s);
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Players</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-3">Squad</h2>
          <ul className="space-y-2">
            {players.map((p) => (
              <li key={p.player_id}>
                <button onClick={() => loadStats(p)} className="w-full text-left px-3 py-2 rounded hover:bg-gray-800">
                  <span className="font-medium">{p.name}</span>
                  <span className="text-gray-400 text-sm ml-2">{p.position} · {p.team}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold mb-3">{selected ? selected.name : "Select a player"}</h2>
          {stats && (
            <pre className="text-sm text-gray-300 bg-black/30 p-3 rounded">{JSON.stringify(stats, null, 2)}</pre>
          )}
        </div>
      </div>
    </div>
  );
}
