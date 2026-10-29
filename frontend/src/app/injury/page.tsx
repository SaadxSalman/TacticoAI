"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

export default function InjuryPage() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    apiGet("/api/v1/injury-risk").then(setData).catch(() => {});
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Injury Risk Assessment</h1>
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="py-2">Player</th>
              <th>Risk Level</th>
              <th>Score</th>
              <th>Load</th>
              <th>History</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.player_id} className="border-b border-gray-800">
                <td className="py-2">{d.name}</td>
                <td className={d.risk_level === "High" ? "text-red-400" : d.risk_level === "Medium" ? "text-yellow-400" : "text-green-400"}>{d.risk_level}</td>
                <td>{Number(d.risk_score).toFixed(2)}</td>
                <td>{d.factors?.load}</td>
                <td>{d.factors?.history}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
