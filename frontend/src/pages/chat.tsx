import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import { chatAI } from "../lib/api";

type Msg = { from: "user" | "bot"; text: string; id: string };

export default function ChatPage() {
  const [log, setLog] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(!!localStorage.getItem("access_token"));
  }, []);

  const send = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg: Msg = { from: "user", text: input, id: Date.now().toString() };
    setLog((l) => [...l, userMsg]);
    setInput("");
    setLoading(true);
    
    try {
      const res = await chatAI(userMsg.text);
      const botMsg: Msg = { from: "bot", text: res.reply, id: (Date.now() + 1).toString() };
      setLog((l) => [...l, botMsg]);
    } catch (error) {
      const botMsg: Msg = { 
        from: "bot", 
        text: "❌ Sorry, something went wrong. Please check your connection and try again.", 
        id: (Date.now() + 1).toString() 
      };
      setLog((l) => [...l, botMsg]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && e.ctrlKey && !loading) {
      send();
    }
  };

  return (
    <main>
      <div className="app-shell">
        <Navbar authed={authed} />
        <div style={{ maxWidth: "900px", margin: "0 auto", padding: "20px" }}>
          <div style={{ marginBottom: "20px", textAlign: "center" }}>
            <h1 className="hero-title" style={{ fontSize: 32, marginBottom: 10 }}>
              DeepVerify Assistant
            </h1>
            <p className="text-muted" style={{ fontSize: 14 }}>
              Powered by Ollama • Discuss news, app features, fact-checking & more
            </p>
          </div>

          <div className="chat-box fade-in" style={{ height: "500px", display: "flex", flexDirection: "column" }}>
            <div className="chat-log" style={{ flex: 1, overflowY: "auto", paddingRight: "10px" }}>
              {log.length === 0 && (
                <div style={{ textAlign: "center", paddingTop: "40px", color: "#666" }}>
                  <p style={{ fontSize: 16, fontWeight: "500", marginBottom: 10 }}>👋 Welcome to DeepVerify Assistant</p>
                  <p className="text-muted" style={{ fontSize: 13, maxWidth: 500, margin: "0 auto" }}>
                    Ask me anything! I can help with:
                    <br />
                    • How to use DeepVerify features
                    <br />
                    • Latest news & current events
                    <br />
                    • Fact-checking tips & media literacy
                    <br />
                    • General questions & conversations
                  </p>
                </div>
              )}
              {log.map((m) => (
                <div key={m.id} style={{ marginBottom: "15px", animation: "fadeIn 0.3s" }}>
                  <div className={`chat-msg ${m.from === "user" ? "chat-user" : "chat-bot"}`} 
                       style={{
                         display: "flex",
                         flexDirection: m.from === "user" ? "row-reverse" : "row",
                         gap: "10px",
                         marginBottom: "8px"
                       }}>
                    <div style={{
                      flex: 1,
                      padding: "12px 16px",
                      borderRadius: "12px",
                      backgroundColor: m.from === "user" ? "#007bff" : "#f0f0f0",
                      color: m.from === "user" ? "white" : "black",
                      lineHeight: "1.5",
                      wordWrap: "break-word"
                    }}>
                      {m.text}
                    </div>
                    {m.from === "bot" && (
                      <button
                        onClick={() => copyToClipboard(m.text, m.id)}
                        style={{
                          background: "none",
                          border: "none",
                          cursor: "pointer",
                          fontSize: 16,
                          padding: "4px 8px",
                          marginTop: "4px"
                        }}
                        title="Copy message"
                      >
                        {copied === m.id ? "✓" : "📋"}
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div style={{ display: "flex", gap: "4px", paddingLeft: "10px" }}>
                  <span style={{
                    width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#999",
                    animation: "bounce 1.4s infinite"
                  }} />
                  <span style={{
                    width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#999",
                    animation: "bounce 1.4s infinite 0.2s"
                  }} />
                  <span style={{
                    width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#999",
                    animation: "bounce 1.4s infinite 0.4s"
                  }} />
                </div>
              )}
            </div>

            <div style={{ borderTop: "1px solid #e5e5e5", paddingTop: "15px", marginTop: "15px" }}>
              <textarea
                className="textarea"
                style={{ 
                  width: "100%",
                  minHeight: 80,
                  padding: "12px",
                  fontSize: 14,
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  fontFamily: "inherit",
                  resize: "vertical"
                }}
                placeholder="Ask me anything... (Ctrl+Enter to send)"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
              />
              <div className="btn-row" style={{ marginTop: "12px", display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                <button 
                  className="btn secondary" 
                  onClick={() => { setLog([]); setInput(""); }}
                  disabled={loading}
                  style={{ opacity: loading ? 0.6 : 1, cursor: loading ? "not-allowed" : "pointer" }}
                >
                  Clear
                </button>
                <button 
                  className="btn" 
                  onClick={send}
                  disabled={!input.trim() || loading}
                  style={{ opacity: !input.trim() || loading ? 0.6 : 1, cursor: !input.trim() || loading ? "not-allowed" : "pointer" }}
                >
                  {loading ? "Thinking..." : "Send"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes bounce {
          0%, 80%, 100% { opacity: 0.5; transform: translateY(0); }
          40% { opacity: 1; transform: translateY(-8px); }
        }
      `}</style>
    </main>
  );
}