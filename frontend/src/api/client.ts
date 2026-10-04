import axios, { AxiosError } from "axios";

export const TOKEN_KEY = "eduadapt.token";

export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err: AxiosError) => {
    if (err.response?.status === 401 && !String(err.config?.url).startsWith("/auth")) {
      localStorage.removeItem(TOKEN_KEY);
      window.location.assign("/login");
    }
    return Promise.reject(err);
  },
);

export function errorMessage(e: unknown): string {
  const err = e as AxiosError<{ detail?: unknown }>;
  const d = err?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x: { msg?: string }) => x.msg).join("; ");
  if (err?.message === "Network Error") return "Can't reach the EduAdapt server. Check that the backend is running.";
  return err?.message || "Something went wrong.";
}
