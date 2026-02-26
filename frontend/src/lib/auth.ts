import { api } from "./api";

export async function signup(name: string, email: string, password: string, language_pref?: string) {
  const res = await api.post("/api/v1/auth/signup", { name, email, password, language_pref });
  saveTokens(res.data); return res.data;
}
export async function login(email: string, password: string) {
  const res = await api.post("/api/v1/auth/login", { email, password });
  saveTokens(res.data); return res.data;
}
export async function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
}
function saveTokens(data: { access_token: string; refresh_token: string }) {
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
  }
}