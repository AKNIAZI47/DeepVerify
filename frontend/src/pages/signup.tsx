import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Navbar from "../components/Navbar";
import { signup } from "../lib/auth";

export default function SignupPage() {
  const [name, setName] = useState("");
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
      await signup(name, email, pw, "en"); 
      router.push("/"); 
    }
    catch (e: any) { 
      const detail = e?.response?.data?.detail;
      if (typeof detail === 'object' && detail !== null) {
        // Handle structured error response
        if (detail.message && detail.errors) {
          setErr(`${detail.message}: ${detail.errors.join(', ')}`);
        } else {
          setErr(JSON.stringify(detail));
        }
      } else {
        setErr(detail || "Signup failed");
      }
    }
  };

  return (
    <main><div className="app-shell">
      <Navbar authed={authed} />
      <h1 className="hero-title" style={{ fontSize: 28 }}>Create Account</h1>
      <div className="form fade-in" style={{ maxWidth: 480 }}>
        <input className="input" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="input" placeholder="Password" type="password" value={pw} onChange={(e) => setPw(e.target.value)} />
        {err && <div className="error">{err}</div>}
        <button className="btn" style={{ width: "100%", marginTop: 8 }} onClick={submit}>Signup</button>
      </div>
    </div></main>
  );
}