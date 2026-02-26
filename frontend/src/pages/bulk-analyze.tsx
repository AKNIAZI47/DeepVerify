import { useState } from 'react';

export default function BulkAnalyze() {
  const [texts, setTexts] = useState<string[]>(['']);
  const [results, setResults] = useState<any[]>([]);

  const addText = () => setTexts([...texts, '']);
  
  const updateText = (index: number, value: string) => {
    const newTexts = [...texts];
    newTexts[index] = value;
    setTexts(newTexts);
  };

  const analyze = async () => {
    const response = await fetch('/api/v1/analyze/batch', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({texts})
    });
    const data = await response.json();
    setResults(data.results || []);
  };

  return (
    <div style={{padding: '2rem'}}>
      <h1>Bulk Analysis</h1>
      {texts.map((text, i) => (
        <textarea
          key={i}
          value={text}
          onChange={(e) => updateText(i, e.target.value)}
          style={{width: '100%', marginBottom: '1rem'}}
        />
      ))}
      <button onClick={addText}>Add Text</button>
      <button onClick={analyze} style={{marginLeft: '1rem'}}>Analyze All</button>
      {results.length > 0 && (
        <div style={{marginTop: '2rem'}}>
          <h2>Results</h2>
          {results.map((r, i) => (
            <div key={i} style={{marginBottom: '1rem', padding: '1rem', border: '1px solid #ccc'}}>
              <strong>{r.verdict}</strong> - {r.confidence}%
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
