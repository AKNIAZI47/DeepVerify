import Link from "next/link";
import { logout } from "../lib/auth";
import { useRouter } from "next/router";
import Logo from "./Logo";

export default function Navbar({ authed }: { authed: boolean }) {
  const router = useRouter();
  return (
    <div className="navbar">
      <Link href="/" className="nav-brand" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Logo className="nav-logo" onClick={() => router.push("/")} />
        <span>DeepVerify</span>
      </Link>
      <div className="nav-links">
        <Link href="/" className="nav-link">Home</Link>
        <Link href="/chat" className="nav-link">DeepVerify Assistant</Link>
        <Link href="/dashboard" className="nav-link">Dashboard</Link>
        {!authed && <Link href="/login" className="nav-link">Login</Link>}
        {!authed && <Link href="/signup" className="nav-btn nav-ghost">Signup</Link>}
        {authed && (
          <button
            onClick={() => { logout(); router.push("/"); }}
            className="nav-btn"
          >
            Logout
          </button>
        )}
      </div>
    </div>
  );
}