import { cookies } from "next/headers";

export const API_INTERNAL_URL = process.env.API_INTERNAL_URL || "http://api:8000";

export async function backendFetch(path: string, init: RequestInit = {}) {
  const store = await cookies();
  const token = store.get("pd_session")?.value;
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  return fetch(`${API_INTERNAL_URL}${path}`, {...init, headers, cache: "no-store"});
}
