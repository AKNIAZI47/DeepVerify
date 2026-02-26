type Item = {
  _id: string;
  query: string;
  verdict: string;
  confidence: number;
  reviewed?: boolean;
  correct?: boolean | null;
};

export default function HistoryItem({ item, onReview }: { item: Item; onReview: (id: string, correct: boolean) => void; }) {
  return (
    <div className="history-item fade-in">
      <div className="history-id">{item._id}</div>
      <div className="history-query">{item.query}</div>
      <div className="history-meta">
        <span>Verdict: <strong>{item.verdict}</strong> • {item.confidence?.toFixed(1)}%</span>
        {item.reviewed ? (
          <span style={{ color: item.correct ? "var(--good)" : "var(--bad)" }}>
            Reviewed: {item.correct ? "Correct" : "Incorrect"}
          </span>
        ) : (
          <div className="review-btns">
            <button className="review-btn good" onClick={() => onReview(item._id, true)}>✅ Correct</button>
            <button className="review-btn bad" onClick={() => onReview(item._id, false)}>❌ Incorrect</button>
          </div>
        )}
      </div>
    </div>
  );
}