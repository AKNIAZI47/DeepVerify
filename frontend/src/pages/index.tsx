import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { api, getStats } from "../lib/api";
import AuthMeter from "../components/AuthMeter";
import SearchBar from "../components/SearchBar";
import SourceCards from "../components/SourceCards";

type Prob = Record<string, number>;

export default function Home() {
  const [authed, setAuthed] = useState(false);
  const [stats, setStats] = useState<any>(null);
  
  // News Analyzer state
  const [input, setInput] = useState("");
  const [html, setHtml] = useState("");
  const [verdict, setVerdict] = useState("");
  const [prob, setProb] = useState<Prob>({});
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<string | null>(null);

  useEffect(() => {
    setAuthed(!!localStorage.getItem("access_token"));
  }, []);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const res = await api.post("/api/v1/analyze", { text: input });
      setVerdict(res.data.verdict);
      setHtml(res.data.html);
      setProb(res.data.scores || {});
      setSources(res.data.sources || []);
      setLanguage(res.data.language || null);
      getStats().then(setStats).catch(() => {});
    } catch (err) {
      console.error(err);
      setVerdict("Error");
      setHtml("<div style='color:red'>Backend error</div>");
      setProb({});
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  const realScore = (prob["Real News"] ?? 0) * 100;
  const fakeScore = (prob["Fake News"] ?? 0) * 100;
  const isReal = realScore >= fakeScore;
  const meterScore = isReal ? realScore : fakeScore;
  const meterLabel = isReal ? "Real" : "Fake";

  return (
    <main>
      <div className="app-shell">
        <Navbar authed={authed} />
        <div className="hero fade-in">
          <div className="hero-kicker">AI-powered verification</div>
          <div className="hero-title">DeepVerify</div>
          <div className="hero-sub">Analyze news text or URLs. See confidence, sources, and save history.</div>
        </div>
        
        {/* News Analyzer */}
        <div className="mt-4">
          {language && <div className="text-xs text-muted mb-2">Detected language: {language}</div>}
          <SearchBar value={input} onChange={setInput} onSubmit={handleAnalyze} loading={loading} />
          
          {verdict && (
            <div className="fade-in" style={{ marginTop: 16 }}>
              <AuthMeter score={meterScore} label={`${meterLabel} • ${(meterScore || 0).toFixed(1)}%`} />
              <div className="grid-2 mt-3">
                <div className="card"><div className="text-muted text-sm">Real</div><div className="hero-title" style={{ fontSize: 22 }}>{realScore.toFixed(1)}%</div></div>
                <div className="card"><div className="text-muted text-sm">Fake</div><div className="hero-title" style={{ fontSize: 22 }}>{fakeScore.toFixed(1)}%</div></div>
              </div>
              <div className="prose-box mt-3" dangerouslySetInnerHTML={{ __html: html }} />
              <SourceCards sources={sources} />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}