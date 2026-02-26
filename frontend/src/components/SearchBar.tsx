type Props = { value: string; onChange: (v: string) => void; onSubmit: () => void; loading: boolean };
export default function SearchBar({ value, onChange, onSubmit, loading }: Props) {
  return (
    <div className="card card-soft fade-in">
      <textarea
        className="textarea"
        placeholder="Paste news text or URL to analyze..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      <div className="btn-row">
        <button className="btn secondary" onClick={() => onChange("")}>Clear</button>
        <button className="btn" onClick={onSubmit} disabled={loading || value.trim().length === 0}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>
    </div>
  );
}