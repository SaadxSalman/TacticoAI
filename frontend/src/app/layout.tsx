import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TacticoAI - Tactical Intelligence",
  description: "Agentic Graph-RAG sports analytics platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0b1020] text-gray-100">
        <div className="flex min-h-screen">
          <aside className="w-64 border-r border-gray-800 bg-[#0f1528] p-6">
            <h1 className="text-2xl font-bold text-blue-400 mb-8">TacticoAI</h1>
            <nav className="space-y-2">
              <a href="/" className="block px-3 py-2 rounded hover:bg-gray-800">Dashboard</a>
              <a href="/query" className="block px-3 py-2 rounded hover:bg-gray-800">Ask AI</a>
              <a href="/players" className="block px-3 py-2 rounded hover:bg-gray-800">Players</a>
              <a href="/tactics" className="block px-3 py-2 rounded hover:bg-gray-800">Tactics</a>
              <a href="/injury" className="block px-3 py-2 rounded hover:bg-gray-800">Injury Risk</a>
            </nav>
          </aside>
          <main className="flex-1 p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}