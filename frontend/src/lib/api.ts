/** Tiny typed fetch client with bearer-token + auto refresh. */
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const ACCESS_KEY = "travelos.access";
const REFRESH_KEY = "travelos.refresh";

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  set({ access_token, refresh_token }: { access_token: string; refresh_token: string }) {
    localStorage.setItem(ACCESS_KEY, access_token);
    localStorage.setItem(REFRESH_KEY, refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function refreshTokens(): Promise<boolean> {
  const refresh_token = tokenStore.refresh;
  if (!refresh_token) return false;
  const resp = await fetch(`${BASE_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });
  if (!resp.ok) return false;
  tokenStore.set(await resp.json());
  return true;
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit & { auth?: boolean; retry?: boolean } = {},
): Promise<T> {
  const { auth = true, retry = true, headers, ...rest } = options;
  const finalHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };
  if (auth && tokenStore.access) {
    finalHeaders.Authorization = `Bearer ${tokenStore.access}`;
  }

  const resp = await fetch(`${BASE_URL}${path}`, { ...rest, headers: finalHeaders });

  if (resp.status === 401 && auth && retry && (await refreshTokens())) {
    return api<T>(path, { ...options, retry: false });
  }

  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(resp.status, detail);
  }

  if (resp.status === 204) return undefined as T;
  return resp.json();
}
