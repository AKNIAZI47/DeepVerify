document.getElementById('analyze').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  
  chrome.scripting.executeScript({
    target: {tabId: tab.id},
    function: () => document.body.innerText
  }, async (results) => {
    const text = results[0].result;
    
    const response = await fetch('http://localhost:8000/api/v1/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    });
    
    const data = await response.json();
    document.getElementById('result').innerHTML = `
      <h3>${data.verdict}</h3>
      <p>Confidence: ${data.confidence}%</p>
    `;
  });
});
