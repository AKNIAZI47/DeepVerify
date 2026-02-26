chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'analyzeText',
    title: 'Analyze with VeriGlow',
    contexts: ['selection']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'analyzeText') {
    const text = info.selectionText;
    // Send to API and show notification
    fetch('http://localhost:8000/api/v1/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    }).then(r => r.json()).then(data => {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: 'VeriGlow Analysis',
        message: `${data.verdict} (${data.confidence}%)`
      });
    });
  }
});
