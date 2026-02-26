type Source = { title: string; url: string; source?: string };
export default function SourceCards({ sources }: { sources: Source[] }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div className="sources fade-in">
      {sources.map((s, i) => (
        <a key={i} className="source-card" href={s.url} target="_blank" rel="noreferrer">
          <div className="text-muted text-xs">{s.source || "Source"}</div>
          <div className="source-title">{s.title || s.url}</div>
          <div className="source-url">{s.url}</div>
        </a>
      ))}
    </div>
  );
}