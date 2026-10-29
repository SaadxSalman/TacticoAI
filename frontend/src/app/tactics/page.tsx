"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

export default function TacticsPage() {
  const [teams, setTeams] = useState<any[]>([]);
  const [selected, setSelected] = useState("T_LIV");
  const [formations, setFormations] = useState<any[]>([]);

  useEffect(() => {
    apiGet("/api/v1/teams").then(setTeams).catch(() => {});
  }, []);

  useEffect(() => {
    apiGet(`/api/v1/teams/${selected}/formations`).then((d) => setFormations(d.formations || [])).catch(() => {});
  }, [selected]);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Tactical Analysis</h1>
      <div className="card mb-6">
        <label className="block mb-2 text-gray-400">Team</label>
        <select value={selected} onChange={(e) => setSelected(e.target.value)} className="px-3 py-2 rounded bg-gray-800 border border-gray-700">
          {teams.map((t) => (
            <option key={t.team_id} value={t.team_id}>{t.name}</option>
          ))}
        </select>
      </div>
      <div className="card">
        <h2 className="text-lg font-semibold mb-3">Formations</h2>
        <ul className="space-y-2">
          {formations.map((f, i) => (
            <li key={i} className="text-gray-300">{f.formation_name}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
