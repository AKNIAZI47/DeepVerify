export default function AuthMeter({ score, label }: { score: number; label: string }) {
  const clamped = Math.max(0, Math.min(100, score));
  return (
    <div className="meter fade-in">
      <div className="meter-top">
        <span>Authenticity Meter</span>
        <span style={{ color: score >= 50 ? "var(--good)" : "var(--bad)" }}>{label}</span>
      </div>
      <div className="meter-bar">
        <div className="meter-fill" style={{ width: `${clamped}%` }} />
      </div>
    </div>
  );
}