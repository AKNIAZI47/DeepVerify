import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { api, getStats, reviewHistory } from "../lib/api";
import HistoryItem from "../components/HistoryItem";

type Item = { _id: string; query: string; verdict: string; confidence: number; reviewed?: boolean; correct?: boolean | null; };

export default function Dashboard() {
  const [items, setItems] = useState<Item[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(!!localStorage.getItem("access_token"));
  }, []);

  const load = async () => {
    const res = await api.get("/api/v1/history");
    setItems(res.data || []);
    getStats().then(setStats).catch(() => {});
  };
  useEffect(() => { load().catch(console.error); }, []);

  const handleReview = async (id: string, correct: boolean) => {
    try { await reviewHistory(id, correct); load(); } catch (e) { console.error(e); }
  };

  return (
    <main><div className="app-shell">
      <Navbar authed={authed} />
      <h1 className="hero-title" style={{ fontSize: 28 }}>Dashboard</h1>
      
      {/* Statistics */}
      {stats && (
        <div className="stats mt-3 fade-in">
          <div className="stat"><div className="stat-label">Users</div><div className="stat-value">{stats.total_users}</div></div>
          <div className="stat"><div className="stat-label">Analyses</div><div className="stat-value">{stats.total_analyses}</div></div>
          <div className="stat"><div className="stat-label">Real</div><div className="stat-value">{stats.total_real}</div></div>
          <div className="stat"><div className="stat-label">Fake</div><div className="stat-value">{stats.total_fake}</div></div>
          <div className="stat"><div className="stat-label">Uncertain</div><div className="stat-value">{stats.total_uncertain}</div></div>
          <div className="stat">
            <div className="stat-label">Accuracy (reviews)</div>
            <div className="stat-value">
              {stats.total_reviews > 0 ? ((stats.correct_votes / stats.total_reviews) * 100).toFixed(1) + "%" : "—"}
            </div>
          </div>
        </div>
      )}
      
      {/* History List */}
      <div className="history-list mt-4">
        <h2 className="text-lg font-semibold mb-2">Analysis History</h2>
        {items.map((it) => <HistoryItem key={it._id} item={it} onReview={handleReview} />)}
        {items.length === 0 && <div className="text-muted">No history yet.</div>}
      </div>
    </div></main>
  );
}