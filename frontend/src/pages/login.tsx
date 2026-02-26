import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Navbar from "../components/Navbar";
import { login } from "../lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  const [authed, setAuthed] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setAuthed(!!localStorage.getItem("access_token"));
  }, []);

  const submit = async () => {
    try { 
      await login(email, pw); 
      router.push("/"); 
    }
    catch (e: any) { 
      const detail = e?.response?.data?.detail;
      if (typeof detail === 'object' && detail !== null) {
        setErr(JSON.stringify(detail));
      } else {
        setErr(detail || "Login failed");
      }
    }
  };

  return (
    <main><div className="app-shell">
      <Navbar authed={authed} />
      <h1 className="hero-title" style={{ fontSize: 28 }}>Login</h1>
      <div className="form fade-in" style={{ maxWidth: 480 }}>
        <input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="input" placeholder="Password" type="password" value={pw} onChange={(e) => setPw(e.target.value)} />
        {err && <div className="error">{err}</div>}
        <button className="btn" style={{ width: "100%", marginTop: 8 }} onClick={submit}>Login</button>
      </div>
    </div></main>
  );
}