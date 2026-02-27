import axios from "axios";
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "https://abdullahniyaxi-deepverify-backend.hf.space";

export const api = axios.create({ 
  baseURL: API_BASE,
  withCredentials: true
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function getStats() { const res = await api.get("/api/v1/stats"); return res.data; }
export async function reviewHistory(history_id: string, correct: boolean) {
  const res = await api.post("/api/v1/history/review", { history_id, correct }); return res.data;
}
export async function chatAI(message: string) {
  const res = await api.post("/api/v1/chat", { message }); return res.data as { reply: string };
}